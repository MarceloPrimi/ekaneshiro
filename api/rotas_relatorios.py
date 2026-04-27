import re

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.dependencias import get_current_admin
from db.database import get_db
from services import sheets_google

router = APIRouter(prefix="/relatorios", tags=["Relatórios"])

_MES_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


@router.post("/exportar", status_code=200, summary="Exportar mês para Google Sheets")
def exportar_para_sheets(
    mes: str = Query(..., description="Mês no formato YYYY-MM, ex: 2026-04"),
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    """
    Cria (ou reutiliza) a planilha do mês e exporta agendamentos + pagamentos.
    Operação idempotente: pode ser chamada várias vezes — os dados são sobrescritos.
    Requer role **admin**.
    """
    if not _MES_RE.match(mes):
        raise HTTPException(
            status_code=422,
            detail="Formato inválido. Use YYYY-MM (ex: 2026-04).",
        )
    try:
        resultado = sheets_google.exportar_mes(db, mes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"service_account.json não encontrado: {exc}",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Erro na integração com Google Sheets: {exc}",
        )
    return resultado
