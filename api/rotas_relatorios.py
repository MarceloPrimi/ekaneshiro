import re
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from api.dependencias import get_current_admin, get_current_user
from db.database import get_db
from db.models import Agendamento, ItemAgendamento, Profissional, ProfissionalServico, Servico
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


@router.get(
    "/clientes-por-profissional",
    summary="Clientes únicos atendidos por profissional",
)
def clientes_por_profissional(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    """
    Retorna a contagem de clientes únicos atendidos por cada profissional,
    considerando apenas agendamentos com status 'concluido'.
    """
    rows = (
        db.query(
            Profissional.id.label("profissional_id"),
            Profissional.nome.label("profissional_nome"),
            func.count(func.distinct(Agendamento.cliente_id)).label("clientes_unicos"),
        )
        .join(ItemAgendamento, ItemAgendamento.profissional_id == Profissional.id)
        .join(Agendamento, Agendamento.id == ItemAgendamento.agendamento_id)
        .filter(Agendamento.status == "concluido")
        .group_by(Profissional.id, Profissional.nome)
        .order_by(func.count(func.distinct(Agendamento.cliente_id)).desc())
        .all()
    )
    return [
        {
            "profissional_id": r.profissional_id,
            "profissional_nome": r.profissional_nome,
            "clientes_unicos": r.clientes_unicos,
        }
        for r in rows
    ]


@router.get(
    "/faturamento",
    summary="Faturamento do mês — global e por profissional",
)
def faturamento_por_mes(
    mes: str = Query(..., description="Mês no formato YYYY-MM"),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    """
    Calcula o faturamento de serviços concluídos em um mês.

    Para cada item de agendamento, o preço usado é:
      COALESCE(profissional_servicos.preco_proprio, servicos.preco)

    Ou seja: se o profissional definiu seu próprio preço para aquele serviço,
    ele é usado. Caso contrário, cai para o preço padrão do catálogo.

    Retorna o total geral + breakdown por profissional.
    """
    if not _MES_RE.match(mes):
        raise HTTPException(
            status_code=422,
            detail="Formato inválido. Use YYYY-MM (ex: 2026-04).",
        )

    ano, mnum = int(mes[:4]), int(mes[5:7])
    inicio = datetime(ano, mnum, 1)
    fim = datetime(ano + 1, 1, 1) if mnum == 12 else datetime(ano, mnum + 1, 1)

    # Preço efetivo = preco_proprio do profissional, ou preco padrão do serviço
    preco_efetivo = func.coalesce(ProfissionalServico.preco_proprio, Servico.preco)

    rows = (
        db.query(
            Profissional.id.label("profissional_id"),
            Profissional.nome.label("profissional_nome"),
            func.sum(preco_efetivo).label("total"),
            func.count(ItemAgendamento.id).label("atendimentos"),
        )
        .select_from(ItemAgendamento)
        .join(Agendamento, Agendamento.id == ItemAgendamento.agendamento_id)
        .join(Profissional, Profissional.id == ItemAgendamento.profissional_id)
        .join(Servico, Servico.id == ItemAgendamento.servico_id)
        # LEFT JOIN para não perder itens cuja associação foi removida mas o agendamento persiste
        .outerjoin(
            ProfissionalServico,
            (ProfissionalServico.profissional_id == ItemAgendamento.profissional_id)
            & (ProfissionalServico.servico_id == ItemAgendamento.servico_id),
        )
        .filter(
            Agendamento.status == "concluido",
            ItemAgendamento.data_hora_inicio >= inicio,
            ItemAgendamento.data_hora_inicio < fim,
        )
        .group_by(Profissional.id, Profissional.nome)
        .order_by(func.sum(preco_efetivo).desc())
        .all()
    )

    por_profissional = [
        {
            "profissional_id": r.profissional_id,
            "profissional_nome": r.profissional_nome,
            "total": float(r.total or 0),
            "atendimentos": r.atendimentos,
        }
        for r in rows
    ]
    total_geral = sum(p["total"] for p in por_profissional)

    return {
        "mes": mes,
        "total_geral": total_geral,
        "por_profissional": por_profissional,
    }

