from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import exists
from sqlalchemy.orm import Session, joinedload, selectinload

from api.dependencias import (
    get_current_admin,
    get_current_recepcionista_ou_admin,
    get_current_user,
)
from db.database import get_db
from db.models import Agendamento, ItemAgendamento, RoleEnum, StatusAgendamentoEnum, Usuario
from schemas.agendamentos import (
    AgendamentoCreate,
    AgendamentoResponse,
    AgendamentoStatusUpdate,
    AgendamentoUpdate,
    PagamentoCreate,
    PagamentoResponse,
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
    current_user: Annotated[Usuario, Depends(get_current_recepcionista_ou_admin)],
):
    return agendamento_service.criar_agendamento(db, payload, criado_por_id=current_user.id)


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

    # Filtro de intervalo de datas via EXISTS — não cria join que duplica linhas
    if data_inicio:
        query = query.filter(
            exists().where(
                (ItemAgendamento.agendamento_id == Agendamento.id)
                & (ItemAgendamento.data_hora_inicio >= data_inicio)
            )
        )
    if data_fim:
        query = query.filter(
            exists().where(
                (ItemAgendamento.agendamento_id == Agendamento.id)
                & (ItemAgendamento.data_hora_inicio <= data_fim)
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
    current_user: Annotated[Usuario, Depends(get_current_recepcionista_ou_admin)],
):
    agendamento = _get_agendamento_ou_404(agendamento_id, db)
    return agendamento_service.atualizar_agendamento(db, agendamento, payload)


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

    # Profissional só pode marcar como Concluído os próprios agendamentos
    from db.models import RoleEnum
    if current_user.role == RoleEnum.profissional:
        if payload.status != StatusAgendamentoEnum.concluido:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Profissionais só podem marcar agendamentos como 'concluído'.",
            )
        profissional_ids = [item.profissional_id for item in agendamento.itens]
        if not current_user.profissional or current_user.profissional.id not in profissional_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você só pode atualizar seus próprios agendamentos.",
            )

    return agendamento_service.atualizar_status(db, agendamento, payload.status)


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
    current_user: Annotated[Usuario, Depends(get_current_recepcionista_ou_admin)],
):
    agendamento = _get_agendamento_ou_404(agendamento_id, db)
    return agendamento_service.registrar_pagamento(
        db, agendamento, payload, registrado_por_id=current_user.id
    )
