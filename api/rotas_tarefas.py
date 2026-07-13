from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from api.dependencias import get_current_user
from db.database import get_db
from db.models import RoleEnum, TarefaInterna, Usuario
from schemas.tarefas import TarefaCreate, TarefaResponse, TarefaUpdate

router = APIRouter(prefix="/tarefas", tags=["Tarefas"])


def _get_ou_404(tarefa_id: int, db: Session) -> TarefaInterna:
    t = db.query(TarefaInterna).filter(TarefaInterna.id == tarefa_id).first()
    if not t:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarefa não encontrada.")
    return t


def _pode_ver(tarefa: TarefaInterna, usuario: Usuario) -> bool:
    if usuario.role in (RoleEnum.admin, RoleEnum.recepcionista):
        return True
    return tarefa.responsavel_id == usuario.id or tarefa.criado_por_id == usuario.id


@router.get("/", response_model=list[TarefaResponse], summary="Listar tarefas internas")
def listar_tarefas(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    query = db.query(TarefaInterna).options(joinedload(TarefaInterna.responsavel))
    if current_user.role == RoleEnum.profissional:
        query = query.filter(
            (TarefaInterna.responsavel_id == current_user.id)
            | (TarefaInterna.criado_por_id == current_user.id)
        )
    return query.order_by(TarefaInterna.data_hora_inicio).all()


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
    data = payload.model_dump()
    # Profissional só pode criar tarefas para si mesmo
    if current_user.role == RoleEnum.profissional:
        data["responsavel_id"] = current_user.id
    nova = TarefaInterna(**data, criado_por_id=current_user.id)
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return nova


@router.patch(
    "/{tarefa_id}",
    response_model=TarefaResponse,
    summary="Atualizar tarefa",
)
def atualizar_tarefa(
    tarefa_id: int,
    payload: TarefaUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    tarefa = _get_ou_404(tarefa_id, db)
    if not _pode_ver(tarefa, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissão para editar esta tarefa.")
    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(tarefa, campo, valor)
    db.commit()
    db.refresh(tarefa)
    return tarefa


@router.delete(
    "/{tarefa_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir tarefa",
)
def excluir_tarefa(
    tarefa_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    tarefa = _get_ou_404(tarefa_id, db)
    if not _pode_ver(tarefa, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissão para excluir esta tarefa.")
    db.delete(tarefa)
    db.commit()
