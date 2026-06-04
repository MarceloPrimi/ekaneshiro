from datetime import datetime

from pydantic import BaseModel, field_validator

from schemas import UTCDatetime

from db.models import RoleEnum


# --- Entrada ---

class UsuarioCreate(BaseModel):
    nome: str
    username: str
    password: str
    role: RoleEnum = RoleEnum.recepcionista

    @field_validator('username')
    @classmethod
    def username_valido(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError('Username deve ter ao menos 3 caracteres.')
        return v


class UsuarioUpdate(BaseModel):
    nome: str | None = None
    username: str | None = None
    ativo: bool | None = None
    role: RoleEnum | None = None

    @field_validator('username')
    @classmethod
    def username_valido(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if len(v) < 3:
            raise ValueError('Username deve ter ao menos 3 caracteres.')
        return v


class AlterarSenhaProprio(BaseModel):
    senha_atual: str
    nova_senha: str


class AlterarSenhaAdmin(BaseModel):
    nova_senha: str


# --- Saída ---

class UsuarioResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    nome: str
    username: str
    role: RoleEnum
    ativo: bool
    criado_em: UTCDatetime


# --- Auth ---

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenFullResponse(BaseModel):
    """Retorna token + dados do usuário em um único round-trip (elimina /me sequencial)."""
    access_token: str
    token_type: str = "bearer"
    user: UsuarioResponse


class TokenData(BaseModel):
    sub: str          # username do usuário
    role: RoleEnum
