from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

from schemas import UTCDatetime

from db.models import StatusAgendamentoEnum
from schemas.categorias_agendamento import CategoriaAgendamentoResponse
from schemas.clientes import ClienteResponse
from schemas.profissionais import ProfissionalResponse
from schemas.servicos import ServicoResponse


# ---------------------------------------------------------------------------
# Mini Etiquetas — catálogo estático de stickers
# ---------------------------------------------------------------------------

MINI_ETIQUETAS_CATALOG: dict[str, str] = {
    "urgente":        "🚀",
    "pago":           "💰",
    "falta_doc":      "⚠️",
    "confirmado":     "✅",
    "retorno":        "🔄",
    "vip":            "⭐",
    "primeira_vez":   "✨",
}

MiniEtiquetaCodigo = Literal[
    "urgente", "pago", "falta_doc", "confirmado", "retorno", "vip", "primeira_vez"
]

# ---------------------------------------------------------------------------
# Recorrência
# ---------------------------------------------------------------------------

class RecurrenceRule(BaseModel):
    """Subconjunto simplificado de RRULE usado no formulário."""
    freq: Literal["weekly", "biweekly", "monthly"]
    count: int | None = Field(default=None, ge=1, le=104)

    def to_rrule(self) -> str:
        mapping = {
            "weekly":   "FREQ=WEEKLY;INTERVAL=1",
            "biweekly": "FREQ=WEEKLY;INTERVAL=2",
            "monthly":  "FREQ=MONTHLY;INTERVAL=1",
        }
        base = mapping[self.freq]
        if self.count is not None:
            base += f";COUNT={self.count}"
        return base


# ---------------------------------------------------------------------------
# Entrada
# ---------------------------------------------------------------------------

class ItemAgendamentoCreate(BaseModel):
    """Um serviço com um profissional em uma data/hora."""
    servico_id: int
    profissional_id: int
    data_hora_inicio: datetime
    # Se fornecido, sobrescreve a duração padrão do serviço
    data_hora_fim: datetime | None = None


class AgendamentoCreate(BaseModel):
    cliente_id: int
    itens: list[ItemAgendamentoCreate]
    cor_hex: str | None = None
    observacoes: str | None = None
    # Novos campos
    categoria_id: int | None = None
    recurrence: RecurrenceRule | None = None
    mini_etiquetas: list[MiniEtiquetaCodigo] | None = None


class AgendamentoStatusUpdate(BaseModel):
    status: StatusAgendamentoEnum


class AgendamentoUpdate(BaseModel):
    cliente_id: int
    itens: list[ItemAgendamentoCreate]
    cor_hex: str | None = None
    observacoes: str | None = None
    # Novos campos
    categoria_id: int | None = None
    recurrence: RecurrenceRule | None = None
    mini_etiquetas: list[MiniEtiquetaCodigo] | None = None
    # "this" = só este; "all" = toda a série
    edit_scope: Literal["this", "all"] = "this"


class AgendamentoCorUpdate(BaseModel):
    cor_hex: str | None = None


# ---------------------------------------------------------------------------
# Saída
# ---------------------------------------------------------------------------

class ItemAgendamentoResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    servico: ServicoResponse
    profissional: ProfissionalResponse
    # Horários de agendamento são tratados como horário local de operação (America/Sao_Paulo).
    # Não usar sufixo UTC (Z), pois isso desloca -3h no frontend ao renderizar.
    data_hora_inicio: datetime
    data_hora_fim: datetime
    google_event_id: str | None


# ---------------------------------------------------------------------------
# Pagamento
# ---------------------------------------------------------------------------

class PagamentoCreate(BaseModel):
    valor: Decimal
    metodo: str   # "pix" | "cartao_credito" | "dinheiro" | etc.
    credito_utilizado: Decimal = Decimal("0.00")


class PagamentoUpdate(BaseModel):
    """Permite corrigir valor e método de um pagamento já registrado (erro de lançamento)."""
    valor: Decimal
    metodo: str
    # Ajuste de crédito utilizado: permite corrigir o campo sem alterar o saldo do cliente
    # automaticamente (o operador deve ajustar o saldo manualmente se necessário).
    credito_utilizado: Decimal = Decimal("0.00")


class PagamentoResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    agendamento_id: int
    valor: Decimal
    metodo: str
    credito_utilizado: Decimal
    pago_em: UTCDatetime


class AgendamentoResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    cliente_id: int
    cliente: ClienteResponse | None = None
    status: StatusAgendamentoEnum
    cor_hex: str | None = None
    observacoes: str | None
    criado_em: UTCDatetime
    itens: list[ItemAgendamentoResponse]
    pagamento: PagamentoResponse | None = None
    # Novos campos
    categoria_id: int | None = None
    categoria: CategoriaAgendamentoResponse | None = None
    recurrence_rule: str | None = None
    parent_id: int | None = None
    mini_etiquetas: list[str] | None = None
    primeira_vez: bool = False

