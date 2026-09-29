from typing import Annotated
import re
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.dependencias import get_current_recepcionista_ou_admin, get_current_user
from db.database import get_db
from db.models import Feriado, Usuario
from pydantic import BaseModel

router = APIRouter(prefix="/feriados", tags=["Feriados"])


class FeriadoCreate(BaseModel):
    data: str            # "YYYY-MM-DD"
    nome: str
    bloquear_agenda: bool = False


class FeriadoPeriodoCreate(BaseModel):
    data_inicio: str     # "YYYY-MM-DD"
    data_fim: str        # "YYYY-MM-DD"
    nome: str
    bloquear_agenda: bool = True


class FeriadoUpdate(BaseModel):
    nome: str | None = None
    bloquear_agenda: bool | None = None


class FeriadoResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    data: str
    nome: str
    bloquear_agenda: bool


class FeriadoPeriodoResponse(BaseModel):
    criados: list[FeriadoResponse]
    atualizados: list[FeriadoResponse]
    total_dias: int


_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _parse_date(value: str, campo: str):
    if not _DATE_RE.match(value):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{campo} deve estar no formato YYYY-MM-DD.",
        )
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{campo} inválida.",
        ) from exc


@router.get("/", response_model=list[FeriadoResponse], summary="Listar feriados")
def listar_feriados(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_user)],
    ano: int | None = None,
):
    query = db.query(Feriado)
    if ano:
        query = query.filter(Feriado.data.startswith(str(ano)))
    return query.order_by(Feriado.data).all()


@router.post(
    "/",
    response_model=FeriadoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar feriado / dia bloqueado (Recepcionista ou Admin)",
)
def criar_feriado(
    payload: FeriadoCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_recepcionista_ou_admin)],
):
    _parse_date(payload.data, "Data")
    existente = db.query(Feriado).filter(Feriado.data == payload.data).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Já existe um feriado em {payload.data}.",
        )
    novo = Feriado(
        data=payload.data,
        nome=payload.nome,
        bloquear_agenda=payload.bloquear_agenda,
        criado_por_id=current_user.id,
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@router.post(
    "/periodo",
    response_model=FeriadoPeriodoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar feriado/recesso em lote (intervalo de datas)",
)
def criar_feriado_periodo(
    payload: FeriadoPeriodoCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_recepcionista_ou_admin)],
):
    inicio = _parse_date(payload.data_inicio, "Data de início")
    fim = _parse_date(payload.data_fim, "Data de fim")
    if fim < inicio:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Data de fim deve ser maior ou igual à data de início.",
        )
    if (fim - inicio).days > 90:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Intervalo máximo de 90 dias por vez.",
        )
    if not payload.nome.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Informe o nome do feriado/recesso.",
        )

    criados: list[Feriado] = []
    atualizados: list[Feriado] = []
    dia = inicio
    while dia <= fim:
        data_str = dia.isoformat()
        existente = db.query(Feriado).filter(Feriado.data == data_str).first()
        if existente:
            existente.nome = payload.nome.strip()
            existente.bloquear_agenda = payload.bloquear_agenda
            atualizados.append(existente)
        else:
            novo = Feriado(
                data=data_str,
                nome=payload.nome.strip(),
                bloquear_agenda=payload.bloquear_agenda,
                criado_por_id=current_user.id,
            )
            db.add(novo)
            criados.append(novo)
        dia += timedelta(days=1)

    db.commit()
    for f in criados + atualizados:
        db.refresh(f)

    return FeriadoPeriodoResponse(
        criados=criados,
        atualizados=atualizados,
        total_dias=len(criados) + len(atualizados),
    )


@router.patch(
    "/{feriado_id}",
    response_model=FeriadoResponse,
    summary="Atualizar feriado (Recepcionista ou Admin)",
)
def atualizar_feriado(
    feriado_id: int,
    payload: FeriadoUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_recepcionista_ou_admin)],
):
    feriado = db.query(Feriado).filter(Feriado.id == feriado_id).first()
    if not feriado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feriado não encontrado.")
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(feriado, field, value)
    db.commit()
    db.refresh(feriado)
    return feriado


@router.delete(
    "/{feriado_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover feriado (Recepcionista ou Admin)",
)
def remover_feriado(
    feriado_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_recepcionista_ou_admin)],
):
    feriado = db.query(Feriado).filter(Feriado.id == feriado_id).first()
    if not feriado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feriado não encontrado.")
    db.delete(feriado)
    db.commit()
