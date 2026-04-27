from pydantic import BaseModel
from decimal import Decimal


class ServicoCreate(BaseModel):
    nome: str
    descricao: str | None = None
    duracao_minutos: int
    preco: Decimal


class ServicoUpdate(BaseModel):
    nome: str | None = None
    descricao: str | None = None
    duracao_minutos: int | None = None
    preco: Decimal | None = None
    ativo: bool | None = None


class ServicoResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    nome: str
    descricao: str | None
    duracao_minutos: int
    preco: Decimal
    ativo: bool
