from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session, joinedload

from api.dependencias import get_current_user
from db.database import get_db
from db.models import Comanda, ItemComanda, PagamentoComanda, StatusComandaEnum, Usuario
from schemas.comandas import (
    ComandaCreate,
    ComandaResponse,
    ItemAgendamentoComandaCreate,
    ItemAvulsoCreate,
    ItemComandaResponse,
    PagamentoComandaCreate,
    PagamentoComandaResponse,
)
from services import comanda_service

router = APIRouter(prefix="/comandas", tags=["Comandas"])

# Opções de eager loading para evitar N+1 nas respostas
_EAGER_COMANDA = [
    joinedload(Comanda.itens).options(
        joinedload(ItemComanda.cliente),
        joinedload(ItemComanda.profissional),
        joinedload(ItemComanda.servico),
    ),
    joinedload(Comanda.pagamentos),
]


def _load_comanda(db: Session, comanda_id: int) -> Comanda:
    from fastapi import HTTPException

    comanda = (
        db.query(Comanda)
        .options(*_EAGER_COMANDA)
        .filter(Comanda.id == comanda_id)
        .first()
    )
    if not comanda:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comanda não encontrada.",
        )
    return comanda


def _to_response(comanda: Comanda) -> ComandaResponse:
    return ComandaResponse.from_orm_with_totals(comanda)


# ---------------------------------------------------------------------------
# Comanda — CRUD principal
# ---------------------------------------------------------------------------

@router.post(
    "/",
    response_model=ComandaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Abrir nova comanda",
)
def abrir_comanda(
    payload: ComandaCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    comanda = comanda_service.abrir_comanda(db, payload, criada_por_id=current_user.id)
    return _to_response(_load_comanda(db, comanda.id))


@router.get(
    "/",
    response_model=list[ComandaResponse],
    summary="Listar comandas",
    description=(
        "Lista comandas com filtros opcionais por status, data e situação de pagamento. "
        "Use pago_filtro para filtrar por comandas pagas (total_pago >= total_itens) ou pendentes."
    ),
)
def listar_comandas(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
    status_filtro: StatusComandaEnum | None = None,
    data_inicio: str | None = None,
    data_fim: str | None = None,
    pago_filtro: str | None = None,
):
    from datetime import datetime, timedelta
    from decimal import Decimal
    
    query = db.query(Comanda).options(*_EAGER_COMANDA)
    
    if status_filtro:
        query = query.filter(Comanda.status == status_filtro)
    
    if data_inicio:
        try:
            dt_inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
            query = query.filter(Comanda.aberta_em >= dt_inicio)
        except ValueError:
            pass
    
    if data_fim:
        try:
            dt_fim = datetime.strptime(data_fim, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(Comanda.aberta_em < dt_fim)
        except ValueError:
            pass
    
    comandas = query.order_by(Comanda.aberta_em.desc()).all()
    
    if pago_filtro:
        resultado = []
        for c in comandas:
            total_itens = sum(
                Decimal(str(i.valor_unitario)) * i.quantidade - Decimal(str(i.desconto))
                for i in c.itens
            )
            total_pago = sum(Decimal(str(p.valor)) for p in c.pagamentos)
            
            if pago_filtro == "pago":
                # Pago: comanda fechada OU (aberta com pagamento completo e itens > 0)
                is_pago = (
                    c.status == StatusComandaEnum.fechada or
                    (total_itens > 0 and total_pago >= total_itens)
                )
                if is_pago:
                    resultado.append(c)
            elif pago_filtro == "pendente":
                # Pendente: comanda aberta com saldo a pagar ou sem itens ainda
                is_pendente = (
                    c.status == StatusComandaEnum.aberta and
                    (total_itens == 0 or total_pago < total_itens)
                )
                if is_pendente:
                    resultado.append(c)
        comandas = resultado
    
    return [_to_response(c) for c in comandas]


@router.get(
    "/{comanda_id}",
    response_model=ComandaResponse,
    summary="Buscar comanda por ID",
)
def buscar_comanda(
    comanda_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    return _to_response(_load_comanda(db, comanda_id))


# ---------------------------------------------------------------------------
# Itens — adicionar agendamento
# ---------------------------------------------------------------------------

@router.post(
    "/{comanda_id}/itens/agendamento",
    response_model=list[ItemComandaResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Adicionar itens de um agendamento à comanda",
    description=(
        "Cada serviço/profissional do agendamento vira uma linha separada na comanda. "
        "Um mesmo ItemAgendamento não pode estar em duas comandas ao mesmo tempo."
    ),
)
def adicionar_itens_agendamento(
    comanda_id: int,
    payload: ItemAgendamentoComandaCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    return comanda_service.adicionar_itens_agendamento(db, comanda_id, payload)


# ---------------------------------------------------------------------------
# Itens — adicionar avulso (serviço ou produto não agendado)
# ---------------------------------------------------------------------------

@router.post(
    "/{comanda_id}/itens/avulso",
    response_model=ItemComandaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Adicionar serviço ou produto avulso à comanda",
    description=(
        "Use para cobrar serviços realizados sem agendamento prévio "
        "ou produtos vendidos no caixa."
    ),
)
def adicionar_item_avulso(
    comanda_id: int,
    payload: ItemAvulsoCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    return comanda_service.adicionar_item_avulso(db, comanda_id, payload)


# ---------------------------------------------------------------------------
# Itens — remover
# ---------------------------------------------------------------------------

@router.delete(
    "/{comanda_id}/itens/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover item da comanda",
)
def remover_item(
    comanda_id: int,
    item_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    comanda_service.remover_item(db, comanda_id, item_id)


# ---------------------------------------------------------------------------
# Pagamentos
# ---------------------------------------------------------------------------

@router.post(
    "/{comanda_id}/pagamentos",
    response_model=PagamentoComandaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar pagamento na comanda",
    description=(
        "Pode ser chamado múltiplas vezes para pagamento dividido "
        "(ex: R$50 PIX + R$30 dinheiro). "
        "Troco em dinheiro é convertido em crédito para o pagador."
    ),
)
def registrar_pagamento(
    comanda_id: int,
    payload: PagamentoComandaCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    return comanda_service.registrar_pagamento(
        db, comanda_id, payload, registrado_por_id=current_user.id
    )


# ---------------------------------------------------------------------------
# Fechar / Cancelar
# ---------------------------------------------------------------------------

@router.post(
    "/{comanda_id}/fechar",
    response_model=ComandaResponse,
    summary="Fechar comanda (checkout)",
    description=(
        "Valida que o total pago cobre o total dos itens e fecha a comanda. "
        "Os agendamentos vinculados são marcados como 'confirmado'."
    ),
)
def fechar_comanda(
    comanda_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    comanda = comanda_service.fechar_comanda(db, comanda_id)
    return _to_response(_load_comanda(db, comanda.id))


@router.post(
    "/{comanda_id}/cancelar",
    response_model=ComandaResponse,
    summary="Cancelar comanda",
    description="Cancela a comanda e estorna créditos consumidos nos pagamentos.",
)
def cancelar_comanda(
    comanda_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    comanda = comanda_service.cancelar_comanda(db, comanda_id)
    return _to_response(_load_comanda(db, comanda.id))
