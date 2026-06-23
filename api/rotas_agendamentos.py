from datetime import date, datetime, time, timedelta
from math import ceil
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import exists
from sqlalchemy.orm import Session, joinedload, selectinload

from api.dependencias import (
    get_current_admin,
    get_current_user,
)
from db.database import get_db
from db.models import Agendamento, ItemAgendamento, RoleEnum, StatusAgendamentoEnum, Usuario
from schemas.agendamentos import (
    AgendamentoCorUpdate,
    AgendamentoCreate,
    AgendamentoResponse,
    AgendamentoStatusUpdate,
    AgendamentoUpdate,
    PagamentoCreate,
    PagamentoResponse,
    PagamentoUpdate,
)
from services import agendamento_service

router = APIRouter(prefix="/agendamentos", tags=["Agendamentos"])

# Opções de eager loading: evitam N+1 queries ao serializar cada agendamento
_EAGER_OPTIONS = [
    joinedload(Agendamento.cliente),
    selectinload(Agendamento.itens).options(
        joinedload(ItemAgendamento.servico),
        joinedload(ItemAgendamento.profissional),
    ),
    joinedload(Agendamento.pagamento),
]


def _verificar_acesso_profissional(current_user: Usuario, agendamento: Agendamento) -> None:
    """Profissional só pode alterar agendamentos que contenham um item seu."""
    if current_user.role == RoleEnum.profissional:
        if not current_user.profissional:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário não vinculado a um profissional.",
            )
        prof_ids = [item.profissional_id for item in agendamento.itens]
        if current_user.profissional.id not in prof_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você só pode alterar seus próprios agendamentos.",
            )


def _get_agendamento_ou_404(agendamento_id: int, db: Session) -> Agendamento:
    agendamento = (
        db.query(Agendamento)
        .options(*_EAGER_OPTIONS)
        .filter(Agendamento.id == agendamento_id)
        .first()
    )
    if not agendamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agendamento não encontrado."
        )
    return agendamento


@router.post(
    "/",
    response_model=AgendamentoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar agendamento (carrinho de serviços)",
)
def criar_agendamento(
    payload: AgendamentoCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    return agendamento_service.criar_agendamento(db, payload, criado_por_id=current_user.id)


MAX_JANELA_DIAS = 93  # ~3 meses; evita queries de 15 meses mantendo uma janela útil centrada em hoje


def _limitar_janela(data_inicio: date, data_fim: date) -> tuple[date, date]:
    """Garante janela <= MAX_JANELA_DIAS.

    Quando a janela pedida contém hoje, recentraliza em torno de hoje para que
    os agendamentos atuais nunca fiquem fora do corte. Sem isso, uma janela de
    '3 meses atrás → 4 meses à frente' seria truncada para
    '3 meses atrás → 3 meses atrás + 93 dias', excluindo a semana atual.
    """
    if (data_fim - data_inicio).days <= MAX_JANELA_DIAS:
        return data_inicio, data_fim
    hoje = date.today()
    if data_inicio <= hoje <= data_fim:
        # Centraliza: metade antes, metade depois de hoje
        meio = MAX_JANELA_DIAS // 2
        novo_inicio = max(data_inicio, hoje - timedelta(days=meio))
        novo_fim = novo_inicio + timedelta(days=MAX_JANELA_DIAS)
        # Ajusta se novo_fim ultrapassar data_fim original
        if novo_fim > data_fim:
            novo_fim = data_fim
            novo_inicio = max(data_inicio, novo_fim - timedelta(days=MAX_JANELA_DIAS))
        return novo_inicio, novo_fim
    # Janela não contém hoje: trunca a partir do início
    return data_inicio, data_inicio + timedelta(days=MAX_JANELA_DIAS)


@router.get("/", response_model=list[AgendamentoResponse], summary="Listar agendamentos")
def listar_agendamentos(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
    cliente_id: int | None = None,
    status_filtro: StatusAgendamentoEnum | None = None,
    profissional_id: int | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
):
    query = db.query(Agendamento).options(*_EAGER_OPTIONS)

    if cliente_id:
        query = query.filter(Agendamento.cliente_id == cliente_id)
    if status_filtro:
        query = query.filter(Agendamento.status == status_filtro)

    # Limitar a janela de datas para evitar queries gigantes (ex: 15 meses → 5.1s wait).
    # Centraliza em torno de hoje quando a janela contém hoje — evita excluir a semana atual.
    # Não aplica limite quando cliente_id está presente (histórico do cliente).
    if not cliente_id and data_inicio and data_fim:
        data_inicio, data_fim = _limitar_janela(data_inicio, data_fim)

    # Filtro de intervalo de datas via EXISTS — não cria join que duplica linhas.
    # data_inicio/data_fim chegam como `date`; convertemos para limites de dia
    # para que o filtro seja inclusivo no dia inteiro (00:00 do início até o
    # último instante do dia final). Sem isso, "data_fim = hoje" excluiria todos
    # os agendamentos de hoje (pois date vira 00:00 e nenhum horário fica <= 00:00).
    if data_inicio:
        inicio_dt = datetime.combine(data_inicio, time.min)
        query = query.filter(
            exists().where(
                (ItemAgendamento.agendamento_id == Agendamento.id)
                & (ItemAgendamento.data_hora_inicio >= inicio_dt)
            )
        )
    if data_fim:
        # Limite superior exclusivo no dia seguinte → cobre todo o dia data_fim.
        fim_dt = datetime.combine(data_fim, time.min) + timedelta(days=1)
        query = query.filter(
            exists().where(
                (ItemAgendamento.agendamento_id == Agendamento.id)
                & (ItemAgendamento.data_hora_inicio < fim_dt)
            )
        )

    # Profissional só enxerga os próprios agendamentos — restrição de role
    if current_user.role == RoleEnum.profissional:
        if not current_user.profissional:
            return []
        filtro_prof_id = current_user.profissional.id
    else:
        # Admin / recepcionista podem usar o filtro opcional
        filtro_prof_id = profissional_id

    # Filtro por profissional via EXISTS — evita join que interfere com eager loading
    if filtro_prof_id:
        query = query.filter(
            exists().where(
                (ItemAgendamento.agendamento_id == Agendamento.id)
                & (ItemAgendamento.profissional_id == filtro_prof_id)
            )
        )

    return query.order_by(Agendamento.criado_em.desc()).all()


@router.get(
    "/{agendamento_id}",
    response_model=AgendamentoResponse,
    summary="Buscar agendamento por ID",
)
def buscar_agendamento(
    agendamento_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_user)],
):
    return _get_agendamento_ou_404(agendamento_id, db)


@router.put(
    "/{agendamento_id}",
    response_model=AgendamentoResponse,
    summary="Editar agendamento completo",
)
def editar_agendamento(
    agendamento_id: int,
    payload: AgendamentoUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    agendamento = _get_agendamento_ou_404(agendamento_id, db)
    _verificar_acesso_profissional(current_user, agendamento)
    return agendamento_service.atualizar_agendamento(db, agendamento, payload, criado_por_id=current_user.id)


@router.patch(
    "/{agendamento_id}/status",
    response_model=AgendamentoResponse,
    summary="Atualizar status do agendamento",
)
def atualizar_status(
    agendamento_id: int,
    payload: AgendamentoStatusUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    agendamento = _get_agendamento_ou_404(agendamento_id, db)
    _verificar_acesso_profissional(current_user, agendamento)
    return agendamento_service.atualizar_status(db, agendamento, payload.status)


@router.patch(
    "/{agendamento_id}/cor",
    response_model=AgendamentoResponse,
    summary="Atualizar cor personalizada do agendamento",
)
def atualizar_cor_agendamento(
    agendamento_id: int,
    payload: AgendamentoCorUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    agendamento = _get_agendamento_ou_404(agendamento_id, db)
    _verificar_acesso_profissional(current_user, agendamento)
    return agendamento_service.atualizar_cor(db, agendamento, payload.cor_hex)


@router.post(
    "/{agendamento_id}/pagamento",
    response_model=PagamentoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar pagamento",
)
def registrar_pagamento(
    agendamento_id: int,
    payload: PagamentoCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    agendamento = _get_agendamento_ou_404(agendamento_id, db)
    _verificar_acesso_profissional(current_user, agendamento)
    return agendamento_service.registrar_pagamento(
        db, agendamento, payload, registrado_por_id=current_user.id
    )


@router.put(
    "/{agendamento_id}/pagamento",
    response_model=PagamentoResponse,
    summary="Editar pagamento já registrado (correção de lançamento)",
)
def editar_pagamento(
    agendamento_id: int,
    payload: PagamentoUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    agendamento = _get_agendamento_ou_404(agendamento_id, db)
    _verificar_acesso_profissional(current_user, agendamento)
    return agendamento_service.editar_pagamento(
        db, agendamento, payload, editado_por_id=current_user.id
    )


@router.delete(
    "/{agendamento_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir agendamento",
)
def excluir_agendamento(
    agendamento_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    agendamento = _get_agendamento_ou_404(agendamento_id, db)
    _verificar_acesso_profissional(current_user, agendamento)
    db.delete(agendamento)
    db.commit()
