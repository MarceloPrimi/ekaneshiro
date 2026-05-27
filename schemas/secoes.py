from pydantic import BaseModel


class SecaoCreate(BaseModel):
    nome: str


class SecaoUpdate(BaseModel):
    nome: str | None = None


class SecaoResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    nome: str


class SecaosProfissionalUpdate(BaseModel):
    secao_ids: list[int]
