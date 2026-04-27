from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from db.models import StatusAgendamentoEnum
from schemas.clientes import ClienteResponse
from schemas.profissionais import ProfissionalResponse
from schemas.servicos import ServicoResponse


# ---------------------------------------------------------------------------
# Entrada
# ---------------------------------------------------------------------------

class ItemAgendamentoCreate(BaseModel):
    """Um serviço com um profissional em uma data/hora."""
    servico_id: int
    profissional_id: int
    data_hora_inicio: datetime


class AgendamentoCreate(BaseModel):
    cliente_id: int
    itens: list[ItemAgendamentoCreate]
    observacoes: str | None = None


class AgendamentoStatusUpdate(BaseModel):
    status: StatusAgendamentoEnum


class AgendamentoUpdate(BaseModel):
    cliente_id: int
    itens: list[ItemAgendamentoCreate]
    observacoes: str | None = None


# ---------------------------------------------------------------------------
# Saída
# ---------------------------------------------------------------------------

class ItemAgendamentoResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    servico: ServicoResponse
    profissional: ProfissionalResponse
    data_hora_inicio: datetime
    data_hora_fim: datetime
    google_event_id: str | None


# ---------------------------------------------------------------------------
# Pagamento
# ---------------------------------------------------------------------------

class PagamentoCreate(BaseModel):
    valor: Decimal
    metodo: str   # "pix" | "cartao_credito" | "dinheiro" | etc.


class PagamentoResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    agendamento_id: int
    valor: Decimal
    metodo: str
    pago_em: datetime


class AgendamentoResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    cliente_id: int
    cliente: ClienteResponse | None = None
    status: StatusAgendamentoEnum
    observacoes: str | None
    criado_em: datetime
    itens: list[ItemAgendamentoResponse]
    pagamento: PagamentoResponse | None = None
