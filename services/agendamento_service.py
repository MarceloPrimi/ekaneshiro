from datetime import datetime, timedelta, timezone
import calendar
import re

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
# Helpers de negócio
# ---------------------------------------------------------------------------

def _is_primeira_vez(db: Session, cliente_id: int) -> bool:
    """Retorna True se este é o primeiro agendamento não-cancelado do cliente."""
    count = (
        db.query(Agendamento)
        .filter(
            Agendamento.cliente_id == cliente_id,
            Agendamento.status != StatusAgendamentoEnum.cancelado,
        )
        .count()
    )
    return count == 0


def _build_mini_etiquetas(
    etiquetas_payload: list[str] | None,
    primeira_vez: bool,
) -> list[str]:
    """Mescla etiquetas manuais com a automática 'primeira_vez'."""
    resultado: list[str] = list(etiquetas_payload or [])
    if primeira_vez and "primeira_vez" not in resultado:
        resultado.insert(0, "primeira_vez")
    return resultado or None


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


def _add_months(dt: datetime, months: int) -> datetime:
    """Add N months to a datetime, clamping day to month-end if necessary."""
    month = dt.month - 1 + months
    year = dt.year + month // 12
    month = month % 12 + 1
    day = min(dt.day, calendar.monthrange(year, month)[1])
    return dt.replace(year=year, month=month, day=day)


def _calcular_deltas_recorrencia(rrule: str, n: int) -> list:
    """Returns list of callables (index -> timedelta or datetime offset) for recurrence."""
    if 'FREQ=MONTHLY' in rrule:
        return [('monthly', i) for i in range(1, n + 1)]
    elif 'INTERVAL=2' in rrule:
        return [('delta', timedelta(weeks=2 * i)) for i in range(1, n + 1)]
    else:
        return [('delta', timedelta(weeks=i)) for i in range(1, n + 1)]


def _aplicar_offset(dt: datetime, offset) -> datetime:
    kind, value = offset
    if kind == 'monthly':
        return _add_months(dt, value)
    return dt + value


def _deletar_filhos(db: Session, parent_id: int) -> None:
    """Deletes all child appointments of a series (cascade removes their itens)."""
    filhos = db.query(Agendamento).filter(Agendamento.parent_id == parent_id).all()
    for filho in filhos:
        db.delete(filho)
    if filhos:
        db.flush()


def _criar_filhos_recorrentes(
    db: Session,
    parent: Agendamento,
    itens_preparados: list,
    rrule: str,
    criado_por_id: int,
) -> None:
    """Creates recurring child appointments for a series."""
    m_count = re.search(r'COUNT=(\d+)', rrule)
    num = int(m_count.group(1)) if m_count else (6 if 'FREQ=MONTHLY' in rrule else 12)
    offsets = _calcular_deltas_recorrencia(rrule, num)

    for offset in offsets:
        filho = Agendamento(
            cliente_id=parent.cliente_id,
            cor_hex=parent.cor_hex,
            observacoes=parent.observacoes,
            criado_por_id=criado_por_id,
            categoria_id=parent.categoria_id,
            recurrence_rule=None,
            parent_id=parent.id,
            mini_etiquetas=parent.mini_etiquetas,
            primeira_vez=False,
        )
        db.add(filho)
        db.flush()

        for item, profissional, servico, fim in itens_preparados:
            novo_inicio = _aplicar_offset(item.data_hora_inicio, offset)
            novo_fim = _aplicar_offset(fim, offset)
            db.add(
                ItemAgendamento(
                    agendamento_id=filho.id,
                    servico_id=servico.id,
                    profissional_id=profissional.id,
                    data_hora_inicio=novo_inicio,
                    data_hora_fim=novo_fim,
                    google_event_id=None,
                )
            )


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


def _checar_conflito_cliente(
    db: Session,
    cliente_id: int,
    inicio: object,
    fim: object,
    excluir_agendamento_id: int | None = None,
) -> None:
    """
    Garante que o cliente não possui outro ItemAgendamento
    que sobreponha o intervalo [inicio, fim).
    """
    query = (
        db.query(ItemAgendamento)
        .join(Agendamento)
        .filter(
            Agendamento.cliente_id == cliente_id,
            Agendamento.status != StatusAgendamentoEnum.cancelado,
            ItemAgendamento.data_hora_inicio < fim,
            ItemAgendamento.data_hora_fim > inicio,
        )
    )
    if excluir_agendamento_id:
        query = query.filter(Agendamento.id != excluir_agendamento_id)
    conflito = query.first()
    if conflito:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Cliente já possui agendamento conflitante "
                f"entre {_fmt_dt(inicio)} e {_fmt_dt(fim)}."
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
        # Respeita data_hora_fim enviada pelo frontend; usa duração padrão caso omitida
        if item.data_hora_fim is not None:
            fim = item.data_hora_fim
            if fim <= item.data_hora_inicio:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="data_hora_fim deve ser posterior a data_hora_inicio.",
                )
        else:
            fim = item.data_hora_inicio + timedelta(minutes=servico.duracao_minutos)
        itens_preparados.append((item, profissional, servico, fim))

    # Cliente pode ter serviços simultâneos; bloqueio permanece apenas por profissional.

    # 2. Calcular primeira_vez ANTES de criar o agendamento (contagem atual = 0)
    eh_primeira_vez = _is_primeira_vez(db, payload.cliente_id)
    etiquetas = _build_mini_etiquetas(
        [str(e) for e in payload.mini_etiquetas] if payload.mini_etiquetas else None,
        eh_primeira_vez,
    )
    rrule = payload.recurrence.to_rrule() if payload.recurrence else None

    # 3. Persistir o cabeçalho do agendamento
    agendamento = Agendamento(
        cliente_id=payload.cliente_id,
        cor_hex=payload.cor_hex,
        observacoes=payload.observacoes,
        criado_por_id=criado_por_id,
        categoria_id=payload.categoria_id,
        recurrence_rule=rrule,
        mini_etiquetas=etiquetas,
        primeira_vez=eh_primeira_vez,
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

    # Gerar ocorrências filhas para agendamentos recorrentes
    if rrule:
        try:
            _criar_filhos_recorrentes(db, agendamento, itens_preparados, rrule, criado_por_id)
            db.commit()
        except Exception:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Erro ao gerar recorrências do agendamento.",
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
    criado_por_id: int | None = None,
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
        if item.data_hora_fim is not None:
            fim = item.data_hora_fim
            if fim <= item.data_hora_inicio:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="data_hora_fim deve ser posterior a data_hora_inicio.",
                )
        else:
            fim = item.data_hora_inicio + timedelta(minutes=servico.duracao_minutos)
        itens_preparados.append((item, profissional, servico, fim))

    # Cliente pode ter serviços simultâneos; bloqueio permanece apenas por profissional.

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
    agendamento.cor_hex = payload.cor_hex
    agendamento.observacoes = payload.observacoes
    agendamento.categoria_id = payload.categoria_id
    new_rrule = payload.recurrence.to_rrule() if payload.recurrence else None
    agendamento.recurrence_rule = new_rrule
    agendamento.mini_etiquetas = (
        [str(e) for e in payload.mini_etiquetas] if payload.mini_etiquetas is not None
        else agendamento.mini_etiquetas
    )
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

    # ── Gerenciar série recorrente ──────────────────────────────────────────
    # Sempre que rrule mudar (adicionada, alterada ou removida), recriar filhos.
    _deletar_filhos(db, agendamento.id)

    if new_rrule:
        _autor = criado_por_id or agendamento.criado_por_id
        try:
            _criar_filhos_recorrentes(db, agendamento, itens_preparados, new_rrule, _autor)
            db.commit()
        except Exception:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Erro ao gerar recorrências do agendamento.",
            )
    else:
        db.commit()  # persiste a deleção de eventuais filhos antigos

    # ── edit_scope = 'all': propagar alterações aos demais filhos da série ──
    # Se este agendamento é um filho (tem parent_id) e o escopo é 'all',
    # redirecionar a edição ao pai e recriar a série toda a partir do pai.
    if getattr(payload, 'edit_scope', 'this') == 'all' and agendamento.parent_id is not None:
        pai = db.query(Agendamento).filter(Agendamento.id == agendamento.parent_id).first()
        if pai:
            pai.cliente_id = agendamento.cliente_id
            pai.cor_hex = agendamento.cor_hex
            pai.observacoes = agendamento.observacoes
            pai.categoria_id = agendamento.categoria_id
            pai.recurrence_rule = new_rrule
            _deletar_filhos(db, pai.id)
            if new_rrule:
                _criar_filhos_recorrentes(
                    db, pai, itens_preparados, new_rrule,
                    criado_por_id or pai.criado_por_id
                )
            db.commit()

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


def atualizar_cor(
    db: Session,
    agendamento: Agendamento,
    cor_hex: str | None,
) -> Agendamento:
    agendamento.cor_hex = cor_hex
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
    from decimal import Decimal
    
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

    cliente = agendamento.cliente
    credito = payload.credito_utilizado

    # Validação e consumo de crédito
    if credito > 0:
        if credito > cliente.saldo_credito:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Crédito insuficiente para abater o valor.",
            )
        cliente.saldo_credito -= credito

    pagamento = Pagamento(
        agendamento_id=agendamento.id,
        valor=payload.valor,
        metodo=payload.metodo,
        credito_utilizado=credito,
        registrado_por_id=registrado_por_id,
    )
    db.add(pagamento)

    # Geração de crédito por troco (quando o pagamento é em dinheiro)
    # 1. Calculamos o valor total dos serviços
    valor_servicos = sum(Decimal(str(item.servico.preco)) for item in agendamento.itens)
    # 2. O valor devido é o total de serviços abatendo o crédito já utilizado
    valor_devido = valor_servicos - credito
    
    if payload.metodo == "dinheiro" and payload.valor > valor_devido:
        troco_credito = payload.valor - valor_devido
        cliente.saldo_credito += troco_credito

    # Pagamento confirma automaticamente o agendamento
    agendamento.status = StatusAgendamentoEnum.confirmado

    db.commit()
    db.refresh(pagamento)
    return pagamento
