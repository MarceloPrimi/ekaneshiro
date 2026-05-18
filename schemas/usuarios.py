from datetime import datetime

from pydantic import BaseModel, EmailStr

from schemas import UTCDatetime

from db.models import RoleEnum


# --- Entrada ---

class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    password: str
    role: RoleEnum = RoleEnum.recepcionista


class UsuarioUpdate(BaseModel):
    nome: str | None = None
    ativo: bool | None = None
    role: RoleEnum | None = None


# --- Saída ---

class UsuarioResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    nome: str
    email: str
    role: RoleEnum
    ativo: bool
    criado_em: UTCDatetime


# --- Auth ---

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    sub: str          # email do usuário
    role: RoleEnum
