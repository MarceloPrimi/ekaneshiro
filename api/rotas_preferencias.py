from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.dependencias import get_current_user
from db.database import get_db
from db.models import PreferenciasUsuario, Usuario

router = APIRouter(prefix="/preferencias", tags=["Preferências"])


class PreferenciasResponse(BaseModel):
    model_config = {"from_attributes": True}
    preset_cores: list[str] | None = None


class PreferenciasUpdate(BaseModel):
    # Lista de até 20 cores hex (ex: ["#59C3B9", "#f59e0b"])
    preset_cores: list[str] | None = None


@router.get("/cores", response_model=PreferenciasResponse, summary="Obter preset de cores do usuário")
def obter_preferencias(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    prefs = (
        db.query(PreferenciasUsuario)
        .filter(PreferenciasUsuario.usuario_id == current_user.id)
        .first()
    )
    if prefs is None:
        return PreferenciasResponse(preset_cores=None)
    return prefs


@router.put("/cores", response_model=PreferenciasResponse, summary="Salvar preset de cores do usuário")
def salvar_preferencias(
    payload: PreferenciasUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    prefs = (
        db.query(PreferenciasUsuario)
        .filter(PreferenciasUsuario.usuario_id == current_user.id)
        .first()
    )
    cores = (payload.preset_cores or [])[:20]  # Limite de 20 cores
    if prefs is None:
        prefs = PreferenciasUsuario(usuario_id=current_user.id, preset_cores=cores)
        db.add(prefs)
    else:
        prefs.preset_cores = cores
    db.commit()
    db.refresh(prefs)
    return prefs
