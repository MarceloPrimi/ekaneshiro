from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from api.dependencias import get_current_admin, get_current_user
from core.security import create_access_token, hash_password, verify_password
from db.database import get_db
from db.models import Usuario
from schemas.usuarios import (
    AlterarSenhaAdmin,
    AlterarSenhaProprio,
    TokenResponse,
    UsuarioCreate,
    UsuarioResponse,
    UsuarioUpdate,
)

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.post("/login", response_model=TokenResponse, summary="Autenticar e obter JWT")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
):
    usuario = (
        db.query(Usuario)
        .filter(Usuario.username == form_data.username, Usuario.ativo == True)
        .first()
    )
    if not usuario or not verify_password(form_data.password, usuario.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token({"sub": usuario.username, "role": usuario.role.value})
    return TokenResponse(access_token=token)


@router.post(
    "/",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar novo usuário (Admin)",
)
def criar_usuario(
    payload: UsuarioCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_admin)],
):
    if db.query(Usuario).filter(Usuario.username == payload.username).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um usuário com este username.",
        )
    novo = Usuario(
        nome=payload.nome,
        username=payload.username,
        hashed_password=hash_password(payload.password),
        role=payload.role,
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@router.get("/me", response_model=UsuarioResponse, summary="Dados do usuário autenticado")
def me(current_user: Annotated[Usuario, Depends(get_current_user)]):
    return current_user


@router.patch("/me/senha", status_code=status.HTTP_204_NO_CONTENT, summary="Alterar própria senha")
def alterar_senha_proprio(
    payload: AlterarSenhaProprio,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    if not verify_password(payload.senha_atual, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta.",
        )
    if len(payload.nova_senha) < 6:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A nova senha deve ter ao menos 6 caracteres.",
        )
    current_user.hashed_password = hash_password(payload.nova_senha)
    db.commit()


@router.get(
    "/",
    response_model=list[UsuarioResponse],
    summary="Listar todos os usuários (Admin)",
)
def listar_usuarios(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_admin)],
):
    return db.query(Usuario).all()


@router.patch(
    "/{usuario_id}",
    response_model=UsuarioResponse,
    summary="Atualizar usuário (Admin)",
)
def atualizar_usuario(
    usuario_id: int,
    payload: UsuarioUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_admin)],
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")

    update_data = payload.model_dump(exclude_unset=True)

    if "username" in update_data:
        conflito = (
            db.query(Usuario)
            .filter(Usuario.username == update_data["username"], Usuario.id != usuario_id)
            .first()
        )
        if conflito:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe um usuário com este username.",
            )

    for field, value in update_data.items():
        setattr(usuario, field, value)

    db.commit()
    db.refresh(usuario)
    return usuario


@router.patch(
    "/{usuario_id}/senha",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Redefinir senha de outro usuário (Admin)",
)
def redefinir_senha_admin(
    usuario_id: int,
    payload: AlterarSenhaAdmin,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_admin)],
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
    if len(payload.nova_senha) < 6:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A nova senha deve ter ao menos 6 caracteres.",
        )
    usuario.hashed_password = hash_password(payload.nova_senha)
    db.commit()


@router.delete(
    "/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover usuário (Admin)",
)
def deletar_usuario(
    usuario_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[Usuario, Depends(get_current_admin)],
):
    if usuario_id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível excluir o próprio usuário.",
        )
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
    db.delete(usuario)
    db.commit()
