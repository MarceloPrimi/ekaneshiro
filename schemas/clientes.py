from datetime import datetime

from pydantic import BaseModel, EmailStr


class ClienteCreate(BaseModel):
    nome: str
    telefone: str | None = None
    email: EmailStr | None = None


class ClienteUpdate(BaseModel):
    nome: str | None = None
    telefone: str | None = None
    email: EmailStr | None = None


class ClienteResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    nome: str
    telefone: str | None
    email: str | None
    criado_em: datetime
