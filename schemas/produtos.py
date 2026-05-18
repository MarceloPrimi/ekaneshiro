from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from schemas import UTCDatetime


class ProdutoCreate(BaseModel):
    nome: str
    descricao: str | None = None
    categoria: str | None = None
    marca: str | None = None
    preco_custo: Decimal | None = None
    preco_venda: Decimal | None = None
    estoque_atual: int = 0
    estoque_minimo: int = 0


class ProdutoUpdate(BaseModel):
    nome: str | None = None
    descricao: str | None = None
    categoria: str | None = None
    marca: str | None = None
    preco_custo: Decimal | None = None
    preco_venda: Decimal | None = None
    estoque_atual: int | None = None
    estoque_minimo: int | None = None
    ativo: bool | None = None


class ProdutoAjusteEstoque(BaseModel):
    """Ajuste pontual de estoque (entrada ou saída)."""
    quantidade: int   # positivo = entrada, negativo = saída
    motivo: str | None = None


class ProdutoResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    nome: str
    descricao: str | None
    categoria: str | None
    marca: str | None
    preco_custo: Decimal | None
    preco_venda: Decimal | None
    estoque_atual: int
    estoque_minimo: int
    ativo: bool
    criado_em: UTCDatetime
    atualizado_em: UTCDatetime | None


class CategoriaProdutoCreate(BaseModel):
    nome: str


class CategoriaProdutoUpdate(BaseModel):
    nome: str | None = None
    ativo: bool | None = None


class CategoriaProdutoResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    nome: str
    ativo: bool
    criado_em: UTCDatetime
