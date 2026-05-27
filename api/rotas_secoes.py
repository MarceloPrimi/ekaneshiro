from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.dependencias import get_current_admin, get_current_user
from db.database import get_db
from db.models import ProfissionalSecao, Secao, Servico, Usuario
from schemas.secoes import SecaoCreate, SecaoResponse, SecaoUpdate

router = APIRouter(prefix="/secoes", tags=["Seções"])


@router.get("/", response_model=list[SecaoResponse])
def listar_secoes(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_user)],
):
    return db.query(Secao).order_by(Secao.nome).all()


@router.post("/", response_model=SecaoResponse, status_code=status.HTTP_201_CREATED)
def criar_secao(
    payload: SecaoCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_admin)],
):
    if db.query(Secao).filter(Secao.nome == payload.nome).first():
        raise HTTPException(status_code=400, detail="Já existe uma seção com este nome.")
    secao = Secao(nome=payload.nome)
    db.add(secao)
    db.commit()
    db.refresh(secao)
    return secao


@router.patch("/{secao_id}", response_model=SecaoResponse)
def atualizar_secao(
    secao_id: int,
    payload: SecaoUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_admin)],
):
    secao = db.query(Secao).filter(Secao.id == secao_id).first()
    if not secao:
        raise HTTPException(status_code=404, detail="Seção não encontrada.")
    if payload.nome is not None:
        secao.nome = payload.nome
    db.commit()
    db.refresh(secao)
    return secao


@router.delete("/{secao_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_secao(
    secao_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_admin)],
):
    secao = db.query(Secao).filter(Secao.id == secao_id).first()
    if not secao:
        raise HTTPException(status_code=404, detail="Seção não encontrada.")
    try:
        # Nullify secao_id on services belonging to this section
        db.query(Servico).filter(Servico.secao_id == secao_id).update(
            {"secao_id": None},
            synchronize_session=False,
        )
        # Remove professional-section links
        db.query(ProfissionalSecao).filter(ProfissionalSecao.secao_id == secao_id).delete(
            synchronize_session=False,
        )
        db.delete(secao)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Não foi possível excluir a seção por conflito de integridade.",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
