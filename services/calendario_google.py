"""
Stub da integração com o Google Calendar.

Enquanto o OAuth 2.0 não estiver configurado, todas as funções retornam
dados fictícios sem falhar, permitindo que o fluxo de agendamento funcione.
Quando a integração real for implementada, basta substituir o corpo das funções
sem alterar as assinaturas — o service de agendamento não precisa mudar.
"""
import logging

logger = logging.getLogger(__name__)


def criar_evento(
    calendar_id: str,
    titulo: str,
    descricao: str,
    inicio: str,   # ISO 8601
    fim: str,      # ISO 8601
) -> str | None:
    """
    Cria um evento no Google Calendar e retorna o event_id.
    Retorna None em caso de falha (o service faz rollback).
    """
    logger.info(
        "[Google Calendar STUB] Evento '%s' em %s → %s (calendar: %s)",
        titulo, inicio, fim, calendar_id,
    )
    # TODO: implementar com google-api-python-client após configurar OAuth
    return f"stub_event_{calendar_id}_{inicio}"


def deletar_evento(calendar_id: str, event_id: str) -> None:
    """Remove um evento do Google Calendar."""
    logger.info(
        "[Google Calendar STUB] Deletar evento %s (calendar: %s)", event_id, calendar_id
    )
    # TODO: implementar com google-api-python-client após configurar OAuth
