from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from core.security import decode_access_token
from db.database import get_db
from db.models import RoleEnum, Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/usuarios/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas ou token expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    username: str | None = payload.get("sub")
    if not username:
        raise credentials_exception

    usuario = db.query(Usuario).filter(Usuario.username == username, Usuario.ativo == True).first()
    if usuario is None:
        raise credentials_exception

    return usuario


def get_current_admin(
    current_user: Annotated[Usuario, Depends(get_current_user)],
) -> Usuario:
    if current_user.role != RoleEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores.",
        )
    return current_user


def get_current_recepcionista_ou_admin(
    current_user: Annotated[Usuario, Depends(get_current_user)],
) -> Usuario:
    if current_user.role not in (RoleEnum.admin, RoleEnum.recepcionista):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a recepcionistas e administradores.",
        )
    return current_user
