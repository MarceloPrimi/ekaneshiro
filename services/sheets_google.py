"""
Google Sheets integration via Service Account.

Architecture:
  - Single fixed spreadsheet (GOOGLE_SPREADSHEET_ID in .env), created by the user
    and shared with the service account as Editor.
  - Monthly tabs: 'Ag-YYYY-MM' (agendamentos) and 'Pag-YYYY-MM' (pagamentos).
  - Only Sheets API is used - no Drive API, no quota issues.
"""
import logging
from datetime import datetime

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from sqlalchemy import extract
from sqlalchemy.orm import Session

from core.config import settings
from db.models import ItemAgendamento, Pagamento

logger = logging.getLogger(__name__)

_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

_HEADER_AGENDAMENTOS = [
    "ID Agend.", "Criado Em", "Cliente", "Status", "Observacoes",
    "Servico", "Profissional", "Inicio", "Fim",
]

_HEADER_PAGAMENTOS = [
    "ID Pagamento", "ID Agend.", "Cliente", "Valor (R$)", "Metodo", "Pago Em",
]

_MESES_PT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Marco", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
}


def _get_sheets_service():
    creds = Credentials.from_service_account_file(
        settings.GOOGLE_SERVICE_ACCOUNT_FILE,
        scopes=_SCOPES,
    )
    return build("sheets", "v4", credentials=creds)


def _get_existing_sheet_ids(svc, spreadsheet_id: str) -> dict:
    spreadsheet = svc.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    return {
        s["properties"]["title"]: s["properties"]["sheetId"]
        for s in spreadsheet.get("sheets", [])
    }


def _garantir_aba(svc, spreadsheet_id: str, titulo: str, existing: dict) -> int:
    if titulo in existing:
        return existing[titulo]
    resp = svc.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": [{"addSheet": {"properties": {"title": titulo}}}]},
    ).execute()
    return resp["replies"][0]["addSheet"]["properties"]["sheetId"]


def exportar_mes(db: Session, mes: str) -> dict:
    """
    Exports agendamentos and pagamentos for a month to the master spreadsheet.
    Creates tabs 'Ag-YYYY-MM' and 'Pag-YYYY-MM' automatically if they do not exist.
    Idempotent: clears and rewrites on every call.

    mes: format 'YYYY-MM'
    """
    if not settings.GOOGLE_SPREADSHEET_ID or settings.GOOGLE_SPREADSHEET_ID == "SEU_ID_AQUI":
        raise ValueError(
            "GOOGLE_SPREADSHEET_ID nao configurado no .env. "
            "Crie a planilha no Google Drive, compartilhe com a service account e cole o ID."
        )

    ano, mes_num = int(mes.split("-")[0]), int(mes.split("-")[1])
    svc = _get_sheets_service()
    spreadsheet_id = settings.GOOGLE_SPREADSHEET_ID

    aba_ag = f"Ag-{mes}"
    aba_pag = f"Pag-{mes}"

    existing = _get_existing_sheet_ids(svc, spreadsheet_id)
    _garantir_aba(svc, spreadsheet_id, aba_ag, existing)
    existing = _get_existing_sheet_ids(svc, spreadsheet_id)
    _garantir_aba(svc, spreadsheet_id, aba_pag, existing)

    # Agendamentos
    itens = (
        db.query(ItemAgendamento)
        .join(ItemAgendamento.agendamento)
        .filter(
            extract("year", ItemAgendamento.data_hora_inicio) == ano,
            extract("month", ItemAgendamento.data_hora_inicio) == mes_num,
        )
        .order_by(ItemAgendamento.data_hora_inicio)
        .all()
    )

    rows_ag = [_HEADER_AGENDAMENTOS]
    for item in itens:
        ag = item.agendamento
        rows_ag.append([
            ag.id,
            ag.criado_em.strftime("%d/%m/%Y %H:%M"),
            ag.cliente.nome if ag.cliente else "",
            ag.status.value,
            ag.observacoes or "",
            item.servico.nome if item.servico else "",
            item.profissional.nome if item.profissional else "",
            item.data_hora_inicio.strftime("%d/%m/%Y %H:%M"),
            item.data_hora_fim.strftime("%d/%m/%Y %H:%M"),
        ])

    # Pagamentos
    pagamentos = (
        db.query(Pagamento)
        .join(Pagamento.agendamento)
        .filter(
            extract("year", Pagamento.pago_em) == ano,
            extract("month", Pagamento.pago_em) == mes_num,
        )
        .order_by(Pagamento.pago_em)
        .all()
    )

    rows_pag = [_HEADER_PAGAMENTOS]
    for pag in pagamentos:
        ag = pag.agendamento
        rows_pag.append([
            pag.id,
            ag.id,
            ag.cliente.nome if ag.cliente else "",
            float(pag.valor),
            pag.metodo,
            pag.pago_em.strftime("%d/%m/%Y %H:%M"),
        ])

    # Clear and rewrite
    svc.spreadsheets().values().batchClear(
        spreadsheetId=spreadsheet_id,
        body={"ranges": [aba_ag, aba_pag]},
    ).execute()

    svc.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            "valueInputOption": "USER_ENTERED",
            "data": [
                {"range": f"{aba_ag}!A1", "values": rows_ag},
                {"range": f"{aba_pag}!A1", "values": rows_pag},
            ],
        },
    ).execute()

    url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
    mes_label = f"{_MESES_PT[mes_num]} {ano}"

    logger.info("Exportacao %s: %d agendamentos, %d pagamentos", mes, len(rows_ag)-1, len(rows_pag)-1)

    return {
        "mes": mes,
        "mes_label": mes_label,
        "spreadsheet_url": url,
        "aba_agendamentos": aba_ag,
        "aba_pagamentos": aba_pag,
        "agendamentos_exportados": len(rows_ag) - 1,
        "pagamentos_exportados": len(rows_pag) - 1,
        "exportado_em": datetime.utcnow().isoformat(),
    }
