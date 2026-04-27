from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from api.dependencias import get_current_admin, get_current_user
from db.database import get_db
from db.models import Servico, Usuario
from schemas.servicos import ServicoCreate, ServicoResponse, ServicoUpdate

router = APIRouter(prefix="/servicos", tags=["Serviços"])


@router.post(
    "/",
    response_model=ServicoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar serviço (Admin)",
)
def criar_servico(
    payload: ServicoCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_admin)],
):
    if db.query(Servico).filter(
        func.lower(Servico.nome) == payload.nome.strip().lower()
    ).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um serviço cadastrado com este nome.",
        )
    novo = Servico(**payload.model_dump())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@router.get("/", response_model=list[ServicoResponse], summary="Listar serviços ativos")
def listar_servicos(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_user)],
    apenas_ativos: bool = True,
):
    query = db.query(Servico)
    if apenas_ativos:
        query = query.filter(Servico.ativo == True)
    return query.order_by(Servico.nome).all()


@router.get("/{servico_id}", response_model=ServicoResponse, summary="Buscar serviço por ID")
def buscar_servico(
    servico_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_user)],
):
    servico = db.query(Servico).filter(Servico.id == servico_id).first()
    if not servico:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Serviço não encontrado.")
    return servico


@router.patch("/{servico_id}", response_model=ServicoResponse, summary="Atualizar serviço (Admin)")
def atualizar_servico(
    servico_id: int,
    payload: ServicoUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_admin)],
):
    servico = db.query(Servico).filter(Servico.id == servico_id).first()
    if not servico:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Serviço não encontrado.")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(servico, field, value)

    db.commit()
    db.refresh(servico)
    return servico


@router.delete(
    "/{servico_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover serviço (Admin)",
)
def deletar_servico(
    servico_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_admin)],
):
    servico = db.query(Servico).filter(Servico.id == servico_id).first()
    if not servico:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Serviço não encontrado.")
    db.delete(servico)
    db.commit()
