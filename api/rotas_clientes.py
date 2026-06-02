from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from api.dependencias import get_current_recepcionista_ou_admin, get_current_user
from db.database import get_db
from db.models import Cliente, Usuario
from schemas.clientes import ClienteCreate, ClienteResponse, ClienteUpdate

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.post(
    "/",
    response_model=ClienteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar cliente",
)
def criar_cliente(
    payload: ClienteCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_recepcionista_ou_admin)],
):
    if payload.email:
        if db.query(Cliente).filter(func.lower(Cliente.email) == payload.email.lower()).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe um cliente cadastrado com este e-mail.",
            )
    if payload.nome and payload.telefone:
        if db.query(Cliente).filter(
            func.lower(Cliente.nome) == payload.nome.strip().lower(),
            Cliente.telefone == payload.telefone.strip(),
        ).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe um cliente com este nome e telefone.",
            )
    novo = Cliente(**payload.model_dump())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@router.get("/", response_model=list[ClienteResponse], summary="Listar clientes")
def listar_clientes(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_user)],
    q: str | None = None,
    limit: int | None = None,
    offset: int = 0,
):
    """
    Lista clientes ordenados por nome.

    - `q`: busca server-side por nome ou telefone (case-insensitive). Evita
      trafegar/renderizar os milhares de clientes só para filtrar no navegador.
    - `limit`/`offset`: paginação opcional. Sem parâmetros, mantém o comportamento
      antigo (retorna todos) para não quebrar telas que ainda dependem disso.
    """
    query = db.query(Cliente)
    if q:
        termo = f"%{q.strip()}%"
        query = query.filter(
            (Cliente.nome.ilike(termo)) | (Cliente.telefone.ilike(termo))
        )
    query = query.order_by(Cliente.nome)
    if offset:
        query = query.offset(offset)
    if limit is not None:
        query = query.limit(limit)
    return query.all()


@router.get("/{cliente_id}", response_model=ClienteResponse, summary="Buscar cliente por ID")
def buscar_cliente(
    cliente_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_user)],
):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado.")
    return cliente


@router.patch("/{cliente_id}", response_model=ClienteResponse, summary="Atualizar cliente")
def atualizar_cliente(
    cliente_id: int,
    payload: ClienteUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_recepcionista_ou_admin)],
):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado.")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(cliente, field, value)

    db.commit()
    db.refresh(cliente)
    return cliente


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Remover cliente")
def deletar_cliente(
    cliente_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_recepcionista_ou_admin)],
):
    from db.models import Agendamento, ItemAgendamento, Pagamento
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado.")
    # remover agendamentos e dependências em cascata
    agendamentos = db.query(Agendamento).filter_by(cliente_id=cliente_id).all()
    for ag in agendamentos:
        db.query(ItemAgendamento).filter_by(agendamento_id=ag.id).delete()
        db.query(Pagamento).filter_by(agendamento_id=ag.id).delete()
        db.delete(ag)
    db.delete(cliente)
    db.commit()
