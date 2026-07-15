from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from db.models import StatusComandaEnum, TipoItemComandaEnum
from schemas import UTCDatetime
from schemas.clientes import ClienteResponse
from schemas.profissionais import ProfissionalResponse
from schemas.servicos import ServicoResponse


# ---------------------------------------------------------------------------
# Criação de comanda
# ---------------------------------------------------------------------------

class ComandaCreate(BaseModel):
    observacoes: str | None = None


# ---------------------------------------------------------------------------
# Itens — vincular agendamento existente
# ---------------------------------------------------------------------------

class ItemAgendamentoComandaCreate(BaseModel):
    """Vincula todos os ItemAgendamento de um agendamento à comanda.

    O sistema busca cada ItemAgendamento do agendamento e cria uma linha
    por serviço/profissional, congelando o preço no momento do lançamento.
    O `valor_unitario` aqui é um override global aplicado a todos os itens
    do agendamento (útil para dar desconto total).
    """
    agendamento_id: int
    cliente_id: int
    valor_unitario_override: Decimal | None = Field(
        default=None,
        description="Se informado, substitui o preço de todos os itens do agendamento.",
    )


# ---------------------------------------------------------------------------
# Itens — serviço/produto avulso (sem agendamento prévio)
# ---------------------------------------------------------------------------

class ItemAvulsoCreate(BaseModel):
    tipo: Literal["servico_avulso", "produto"] = "servico_avulso"
    cliente_id: int
    profissional_id: int | None = None
    servico_id: int | None = None
    descricao: str | None = None
    valor_unitario: Decimal
    quantidade: int = Field(default=1, ge=1)
    desconto: Decimal = Decimal("0.00")

    @model_validator(mode="after")
    def validar_descricao_ou_servico(self) -> "ItemAvulsoCreate":
        if self.servico_id is None and not self.descricao:
            raise ValueError(
                "Informe 'servico_id' ou 'descricao' para o item avulso."
            )
        return self


# ---------------------------------------------------------------------------
# Pagamento da comanda
# ---------------------------------------------------------------------------

class PagamentoComandaCreate(BaseModel):
    valor: Decimal
    metodo: str
    credito_utilizado: Decimal = Decimal("0.00")
    # Se None, o crédito/troco é vinculado ao primeiro cliente dos itens
    pagador_cliente_id: int | None = None


# ---------------------------------------------------------------------------
# Respostas
# ---------------------------------------------------------------------------

class ItemComandaResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    tipo: TipoItemComandaEnum
    agendamento_id: int | None
    item_agendamento_id: int | None
    cliente: ClienteResponse
    profissional: ProfissionalResponse | None
    servico: ServicoResponse | None
    descricao: str | None
    valor_unitario: Decimal
    quantidade: int
    desconto: Decimal

    @property
    def subtotal(self) -> Decimal:
        return self.valor_unitario * self.quantidade - self.desconto


class PagamentoComandaResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    valor: Decimal
    metodo: str
    credito_utilizado: Decimal
    pagador_cliente_id: int | None
    pago_em: UTCDatetime


class ComandaResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    status: StatusComandaEnum
    observacoes: str | None
    aberta_em: UTCDatetime
    fechada_em: UTCDatetime | None
    itens: list[ItemComandaResponse]
    pagamentos: list[PagamentoComandaResponse]
    total_itens: Decimal = Decimal("0.00")
    total_pago: Decimal = Decimal("0.00")
    saldo_restante: Decimal = Decimal("0.00")

    @classmethod
    def from_orm_with_totals(cls, comanda) -> "ComandaResponse":
        """Constrói o response calculando os totais financeiros."""
        total_itens = sum(
            item.valor_unitario * item.quantidade - item.desconto
            for item in comanda.itens
        )
        total_pago = sum(p.valor for p in comanda.pagamentos)
        obj = cls.model_validate(comanda)
        obj.total_itens = total_itens
        obj.total_pago = total_pago
        obj.saldo_restante = total_itens - total_pago
        return obj
