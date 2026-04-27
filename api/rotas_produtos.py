from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.dependencias import get_current_recepcionista_ou_admin, get_current_user
from db.database import get_db
from db.models import CategoriaProduto, Produto, Usuario
from schemas.produtos import (
    CategoriaProdutoCreate, CategoriaProdutoResponse, CategoriaProdutoUpdate,
    ProdutoAjusteEstoque, ProdutoCreate, ProdutoResponse, ProdutoUpdate,
)

router = APIRouter(prefix="/produtos", tags=["Produtos"])


def _get_produto_ou_404(produto_id: int, db: Session) -> Produto:
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado.")
    return produto


@router.get("/", response_model=list[ProdutoResponse], summary="Listar produtos")
def listar_produtos(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_user)],
    apenas_ativos: bool = Query(True),
    categoria: str | None = Query(None),
):
    query = db.query(Produto)
    if apenas_ativos:
        query = query.filter(Produto.ativo == True)
    if categoria:
        query = query.filter(Produto.categoria == categoria)
    return query.order_by(Produto.nome).all()


@router.post(
    "/",
    response_model=ProdutoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar produto",
)
def criar_produto(
    payload: ProdutoCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_recepcionista_ou_admin)],
):
    produto = Produto(**payload.model_dump())
    db.add(produto)
    db.commit()
    db.refresh(produto)
    return produto


# ---------------------------------------------------------------------------
# Rotas de Categorias
# ---------------------------------------------------------------------------

@router.get("/categorias/", response_model=list[CategoriaProdutoResponse], summary="Listar categorias")
def listar_categorias(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_user)],
    apenas_ativas: bool = Query(False),
):
    query = db.query(CategoriaProduto)
    if apenas_ativas:
        query = query.filter(CategoriaProduto.ativo == True)
    return query.order_by(CategoriaProduto.nome).all()


@router.post(
    "/categorias/",
    response_model=CategoriaProdutoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar categoria",
)
def criar_categoria(
    payload: CategoriaProdutoCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_recepcionista_ou_admin)],
):
    existente = db.query(CategoriaProduto).filter(CategoriaProduto.nome == payload.nome).first()
    if existente:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Categoria já existe.")
    categoria = CategoriaProduto(nome=payload.nome)
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    return categoria


@router.patch("/categorias/{categoria_id}", response_model=CategoriaProdutoResponse, summary="Editar categoria")
def editar_categoria(
    categoria_id: int,
    payload: CategoriaProdutoUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_recepcionista_ou_admin)],
):
    categoria = db.query(CategoriaProduto).filter(CategoriaProduto.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada.")
    if payload.nome is not None and payload.nome != categoria.nome:
        dup = db.query(CategoriaProduto).filter(CategoriaProduto.nome == payload.nome).first()
        if dup:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe uma categoria com esse nome.")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(categoria, field, value)
    db.commit()
    db.refresh(categoria)
    return categoria


@router.delete("/categorias/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Excluir categoria")
def excluir_categoria(
    categoria_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_recepcionista_ou_admin)],
):
    categoria = db.query(CategoriaProduto).filter(CategoriaProduto.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada.")
    db.delete(categoria)
    db.commit()


# ---------------------------------------------------------------------------
# Rotas de Produtos por ID
# ---------------------------------------------------------------------------


def buscar_produto(
    produto_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_user)],
):
    return _get_produto_ou_404(produto_id, db)


@router.patch("/{produto_id}", response_model=ProdutoResponse, summary="Editar produto")
def editar_produto(
    produto_id: int,
    payload: ProdutoUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_recepcionista_ou_admin)],
):
    produto = _get_produto_ou_404(produto_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(produto, field, value)
    db.commit()
    db.refresh(produto)
    return produto


@router.post(
    "/{produto_id}/ajuste",
    response_model=ProdutoResponse,
    summary="Ajustar estoque (entrada ou saída)",
)
def ajustar_estoque(
    produto_id: int,
    payload: ProdutoAjusteEstoque,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_recepcionista_ou_admin)],
):
    produto = _get_produto_ou_404(produto_id, db)
    novo_estoque = produto.estoque_atual + payload.quantidade
    if novo_estoque < 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Estoque insuficiente. Atual: {produto.estoque_atual}, ajuste: {payload.quantidade}.",
        )
    produto.estoque_atual = novo_estoque
    db.commit()
    db.refresh(produto)
    return produto


@router.delete("/{produto_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Excluir produto")
def excluir_produto(
    produto_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_recepcionista_ou_admin)],
):
    produto = _get_produto_ou_404(produto_id, db)
    db.delete(produto)
    db.commit()
