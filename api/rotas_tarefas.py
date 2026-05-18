from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.dependencias import get_current_user
from db.database import get_db
from db.models import TarefaInterna, Usuario
from schemas.tarefas import TarefaCreate, TarefaResponse, TarefaUpdate

router = APIRouter(prefix="/tarefas", tags=["Tarefas"])


def _get_ou_404(tarefa_id: int, db: Session) -> TarefaInterna:
    t = db.query(TarefaInterna).filter(TarefaInterna.id == tarefa_id).first()
    if not t:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarefa não encontrada.")
    return t


@router.get("/", response_model=list[TarefaResponse], summary="Listar tarefas internas")
def listar_tarefas(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_user)],
):
    return db.query(TarefaInterna).order_by(TarefaInterna.data_hora_inicio).all()


@router.post(
    "/",
    response_model=TarefaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar tarefa interna",
)
def criar_tarefa(
    payload: TarefaCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    nova = TarefaInterna(**payload.model_dump(), criado_por_id=current_user.id)
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return nova


@router.patch("/{tarefa_id}", response_model=TarefaResponse, summary="Atualizar tarefa")
def atualizar_tarefa(
    tarefa_id: int,
    payload: TarefaUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_user)],
):
    tarefa = _get_ou_404(tarefa_id, db)
    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(tarefa, campo, valor)
    db.commit()
    db.refresh(tarefa)
    return tarefa


@router.delete("/{tarefa_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Excluir tarefa")
def excluir_tarefa(
    tarefa_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_user)],
):
    tarefa = _get_ou_404(tarefa_id, db)
    db.delete(tarefa)
    db.commit()
