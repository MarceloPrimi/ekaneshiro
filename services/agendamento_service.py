from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from db.models import (
    Agendamento,
    ItemAgendamento,
    Pagamento,
    Profissional,
    ProfissionalServico,
    Servico,
    StatusAgendamentoEnum,
)
from schemas.agendamentos import AgendamentoCreate, PagamentoCreate
from services import calendario_google


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

_BRT = timezone(timedelta(hours=-3))


def _fmt_dt(dt) -> str:
    """Formata um datetime (UTC ou naive) em horário de Brasília legível."""
    if dt is None:
        return '?'
    if isinstance(dt, datetime) and dt.tzinfo is not None:
        dt = dt.astimezone(_BRT)
    if isinstance(dt, datetime):
        return dt.strftime('%d/%m/%Y %H:%M')
    return str(dt)


# ---------------------------------------------------------------------------
# Helpers de validação
# ---------------------------------------------------------------------------

def _validar_profissional_habilitado(
    db: Session, profissional_id: int, servico_id: int
) -> tuple[Profissional, Servico]:
    profissional = (
        db.query(Profissional)
        .filter(Profissional.id == profissional_id, Profissional.ativo == True)
        .first()
    )
    if not profissional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profissional {profissional_id} não encontrado ou inativo.",
        )

    servico = (
        db.query(Servico)
        .filter(Servico.id == servico_id, Servico.ativo == True)
        .first()
    )
    if not servico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Serviço {servico_id} não encontrado ou inativo.",
        )

    vinculo = (
        db.query(ProfissionalServico)
        .filter_by(profissional_id=profissional_id, servico_id=servico_id)
        .first()
    )
    if not vinculo:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Profissional '{profissional.nome}' não está habilitado "
                f"para o serviço '{servico.nome}'."
            ),
        )

    return profissional, servico


def _checar_conflito(
    db: Session,
    profissional_id: int,
    inicio: object,
    fim: object,
    excluir_item_id: int | None = None,
) -> None:
    """
    Garante que o profissional não possui outro ItemAgendamento
    que sobreponha o intervalo [inicio, fim).

    Condição de sobreposição:
        existente.inicio < novo.fim  AND  existente.fim > novo.inicio
    """
    query = (
        db.query(ItemAgendamento)
        .join(Agendamento)
        .filter(
            ItemAgendamento.profissional_id == profissional_id,
            Agendamento.status != StatusAgendamentoEnum.cancelado,
            ItemAgendamento.data_hora_inicio < fim,
            ItemAgendamento.data_hora_fim > inicio,
        )
    )
    if excluir_item_id:
        query = query.filter(ItemAgendamento.id != excluir_item_id)

    if query.first():
        profissional_obj = db.get(Profissional, profissional_id)
        nome = profissional_obj.nome if profissional_obj else str(profissional_id)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"{nome} já possui agendamento "
                f"conflitante entre {_fmt_dt(inicio)} e {_fmt_dt(fim)}."
            ),
        )


# ---------------------------------------------------------------------------
# Criação de agendamento (transação ACID completa)
# ---------------------------------------------------------------------------

def criar_agendamento(
    db: Session,
    payload: AgendamentoCreate,
    criado_por_id: int,
) -> Agendamento:
    if not payload.itens:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="O agendamento deve ter pelo menos um item.",
        )

    # 1. Validar todos os itens ANTES de qualquer inserção
    itens_preparados = []
    for item in payload.itens:
        profissional, servico = _validar_profissional_habilitado(
            db, item.profissional_id, item.servico_id
        )
        fim = item.data_hora_inicio + timedelta(minutes=servico.duracao_minutos)
        _checar_conflito(db, item.profissional_id, item.data_hora_inicio, fim)
        itens_preparados.append((item, profissional, servico, fim))

    # 2. Persistir o cabeçalho do agendamento
    agendamento = Agendamento(
        cliente_id=payload.cliente_id,
        observacoes=payload.observacoes,
        criado_por_id=criado_por_id,
    )
    db.add(agendamento)
    db.flush()  # Gera o ID sem commitar ainda

    # 3. Persistir os itens e chamar o Google Calendar
    eventos_criados: list[tuple[str, str]] = []  # (calendar_id, event_id) para rollback

    try:
        for item, profissional, servico, fim in itens_preparados:
            event_id = None
            if profissional.google_calendar_id:
                event_id = calendario_google.criar_evento(
                    calendar_id=profissional.google_calendar_id,
                    titulo=f"{servico.nome} — {agendamento.cliente_id}",
                    descricao=payload.observacoes or "",
                    inicio=item.data_hora_inicio.isoformat(),
                    fim=fim.isoformat(),
                )
                if event_id is None:
                    raise RuntimeError(
                        f"Falha ao criar evento no Google Calendar "
                        f"para profissional {profissional.id}."
                    )
                eventos_criados.append((profissional.google_calendar_id, event_id))

            db.add(
                ItemAgendamento(
                    agendamento_id=agendamento.id,
                    servico_id=servico.id,
                    profissional_id=profissional.id,
                    data_hora_inicio=item.data_hora_inicio,
                    data_hora_fim=fim,
                    google_event_id=event_id,
                )
            )

        db.commit()

    except Exception:
        db.rollback()
        # Tenta desfazer eventos já criados no Google Calendar
        for cal_id, ev_id in eventos_criados:
            try:
                calendario_google.deletar_evento(cal_id, ev_id)
            except Exception:
                pass  # Log será feito pelo stub/implementação real
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Erro ao sincronizar com o Google Calendar. Agendamento não foi salvo.",
        )

    db.refresh(agendamento)
    return agendamento


# ---------------------------------------------------------------------------
# Atualização completa (edição)
# ---------------------------------------------------------------------------

def atualizar_agendamento(
    db: Session,
    agendamento: Agendamento,
    payload,  # AgendamentoUpdate
) -> Agendamento:
    from schemas.agendamentos import AgendamentoUpdate  # evitar import circular

    if not payload.itens:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="O agendamento deve ter pelo menos um item.",
        )

    # 1. Validar novos itens
    itens_preparados = []
    for item in payload.itens:
        profissional, servico = _validar_profissional_habilitado(
            db, item.profissional_id, item.servico_id
        )
        fim = item.data_hora_inicio + timedelta(minutes=servico.duracao_minutos)
        # Para edição: ignorar conflitos com itens do próprio agendamento
        # Passamos excluir_item_id=None pois os itens antigos serão deletados antes;
        # basta checar contra todos os outros agendamentos exceto o atual.
        # Usamos um filtro customizado via subquery no lugar de _checar_conflito.
        conflito_query = (
            db.query(ItemAgendamento)
            .join(Agendamento)
            .filter(
                ItemAgendamento.profissional_id == item.profissional_id,
                Agendamento.status != StatusAgendamentoEnum.cancelado,
                Agendamento.id != agendamento.id,
                ItemAgendamento.data_hora_inicio < fim,
                ItemAgendamento.data_hora_fim > item.data_hora_inicio,
            )
        )
        if conflito_query.first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"{profissional.nome} já possui agendamento conflitante entre {_fmt_dt(item.data_hora_inicio)} e {_fmt_dt(fim)}.",
            )
        itens_preparados.append((item, profissional, servico, fim))

    # 2. Remover eventos antigos do Google Calendar
    for item_antigo in agendamento.itens:
        if item_antigo.google_event_id and item_antigo.profissional.google_calendar_id:
            try:
                calendario_google.deletar_evento(
                    item_antigo.profissional.google_calendar_id,
                    item_antigo.google_event_id,
                )
            except Exception:
                pass

    # 3. Remover itens antigos do banco
    for item_antigo in list(agendamento.itens):
        db.delete(item_antigo)
    db.flush()

    # 4. Atualizar cabeçalho
    agendamento.cliente_id = payload.cliente_id
    agendamento.observacoes = payload.observacoes
    db.flush()

    # 5. Inserir novos itens + Google Calendar
    eventos_criados: list[tuple[str, str]] = []
    try:
        for item, profissional, servico, fim in itens_preparados:
            event_id = None
            if profissional.google_calendar_id:
                event_id = calendario_google.criar_evento(
                    calendar_id=profissional.google_calendar_id,
                    titulo=f"{servico.nome} — {agendamento.cliente_id}",
                    descricao=payload.observacoes or "",
                    inicio=item.data_hora_inicio.isoformat(),
                    fim=fim.isoformat(),
                )
                if event_id is None:
                    raise RuntimeError("Falha ao criar evento no Google Calendar.")
                eventos_criados.append((profissional.google_calendar_id, event_id))

            db.add(
                ItemAgendamento(
                    agendamento_id=agendamento.id,
                    servico_id=servico.id,
                    profissional_id=profissional.id,
                    data_hora_inicio=item.data_hora_inicio,
                    data_hora_fim=fim,
                    google_event_id=event_id,
                )
            )

        db.commit()
    except Exception:
        db.rollback()
        for cal_id, ev_id in eventos_criados:
            try:
                calendario_google.deletar_evento(cal_id, ev_id)
            except Exception:
                pass
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Erro ao sincronizar com o Google Calendar. Edição não foi salva.",
        )

    db.refresh(agendamento)
    return agendamento


# ---------------------------------------------------------------------------
# Atualização de status
# ---------------------------------------------------------------------------

def atualizar_status(
    db: Session,
    agendamento: Agendamento,
    novo_status: StatusAgendamentoEnum,
) -> Agendamento:
    agendamento.status = novo_status

    # Se cancelado, remove os eventos do Google Calendar
    if novo_status == StatusAgendamentoEnum.cancelado:
        for item in agendamento.itens:
            if item.google_event_id and item.profissional.google_calendar_id:
                try:
                    calendario_google.deletar_evento(
                        item.profissional.google_calendar_id,
                        item.google_event_id,
                    )
                except Exception:
                    pass  # Não bloqueia o cancelamento por falha no Calendar

    db.commit()
    db.refresh(agendamento)
    return agendamento


# ---------------------------------------------------------------------------
# Registro de pagamento
# ---------------------------------------------------------------------------

def registrar_pagamento(
    db: Session,
    agendamento: Agendamento,
    payload: PagamentoCreate,
    registrado_por_id: int,
) -> Pagamento:
    if agendamento.pagamento:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este agendamento já possui pagamento registrado.",
        )
    if agendamento.status == StatusAgendamentoEnum.cancelado:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Não é possível registrar pagamento em agendamento cancelado.",
        )

    pagamento = Pagamento(
        agendamento_id=agendamento.id,
        valor=payload.valor,
        metodo=payload.metodo,
        registrado_por_id=registrado_por_id,
    )
    db.add(pagamento)

    # Pagamento confirma automaticamente o agendamento
    agendamento.status = StatusAgendamentoEnum.confirmado

    db.commit()
    db.refresh(pagamento)
    return pagamento
