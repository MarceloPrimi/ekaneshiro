from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr

from schemas import UTCDatetime


class ClienteCreate(BaseModel):
    nome: str
    telefone: str | None = None
    email: EmailStr | None = None
    observacoes: str | None = None
    campos_dinamicos: dict[str, Any] | list | None = None


class ClienteUpdate(BaseModel):
    nome: str | None = None
    telefone: str | None = None
    email: EmailStr | None = None
    observacoes: str | None = None
    campos_dinamicos: dict[str, Any] | list | None = None


class ClienteResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    nome: str
    telefone: str | None
    email: str | None
    observacoes: str | None = None
    campos_dinamicos: dict[str, Any] | list | None = None
    criado_em: UTCDatetime
