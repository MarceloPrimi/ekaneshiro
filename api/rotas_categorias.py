from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.dependencias import get_current_recepcionista_ou_admin, get_current_user
from db.database import get_db
from db.models import CategoriaAgendamento, Usuario
from schemas.categorias_agendamento import (
    CategoriaAgendamentoCreate,
    CategoriaAgendamentoResponse,
    CategoriaAgendamentoUpdate,
)

router = APIRouter(prefix="/categorias-agendamento", tags=["Categorias de Agendamento"])


def _get_ou_404(cat_id: int, db: Session) -> CategoriaAgendamento:
    cat = db.get(CategoriaAgendamento, cat_id)
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada.")
    return cat


@router.get(
    "/",
    response_model=list[CategoriaAgendamentoResponse],
    summary="Listar categorias de agendamento",
)
def listar_categorias(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_user)],
    apenas_ativas: bool = True,
):
    query = db.query(CategoriaAgendamento)
    if apenas_ativas:
        query = query.filter(CategoriaAgendamento.ativo == True)
    return query.order_by(CategoriaAgendamento.nome).all()


@router.post(
    "/",
    response_model=CategoriaAgendamentoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar categoria de agendamento",
)
def criar_categoria(
    payload: CategoriaAgendamentoCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_recepcionista_ou_admin)],
):
    if db.query(CategoriaAgendamento).filter_by(nome=payload.nome).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Já existe uma categoria com o nome '{payload.nome}'.",
        )
    cat = CategoriaAgendamento(nome=payload.nome, cor_hex=payload.cor_hex)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.patch(
    "/{cat_id}",
    response_model=CategoriaAgendamentoResponse,
    summary="Editar categoria de agendamento",
)
def editar_categoria(
    cat_id: int,
    payload: CategoriaAgendamentoUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_recepcionista_ou_admin)],
):
    cat = _get_ou_404(cat_id, db)
    if payload.nome is not None:
        existente = db.query(CategoriaAgendamento).filter(
            CategoriaAgendamento.nome == payload.nome,
            CategoriaAgendamento.id != cat_id,
        ).first()
        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Já existe uma categoria com o nome '{payload.nome}'.",
            )
        cat.nome = payload.nome
    if payload.cor_hex is not None:
        cat.cor_hex = payload.cor_hex
    if payload.ativo is not None:
        cat.ativo = payload.ativo
    db.commit()
    db.refresh(cat)
    return cat


@router.delete(
    "/{cat_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir (desativar) categoria de agendamento",
)
def excluir_categoria(
    cat_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_recepcionista_ou_admin)],
):
    cat = _get_ou_404(cat_id, db)
    # Soft-delete: apenas desativa para não quebrar FKs existentes
    cat.ativo = False
    db.commit()
