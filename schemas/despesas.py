from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from schemas import UTCDatetime


class CategoriaDespesaCreate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)


class CategoriaDespesaResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    nome: str
    ativo: bool
    criado_em: UTCDatetime


class DespesaCreate(BaseModel):
    data_pagamento: date | None = None
    data_vencimento: date | None = None
    descricao: str = Field(..., min_length=1, max_length=300)
    categoria_id: int
    status: str = "pendente"  # pago | pendente
    valor: Decimal = Field(..., gt=0)
    recorrencia: str = "avulsa"  # avulsa | mensal | temporaria
    vigencia_inicio: date | None = None
    vigencia_fim: date | None = None

    @model_validator(mode="after")
    def validar_regras(self):
        status = (self.status or "").strip().lower()
        rec = (self.recorrencia or "avulsa").strip().lower()
        self.recorrencia = rec

        if rec == "avulsa":
            if status == "pago" and self.data_pagamento is None:
                raise ValueError("Data do pagamento é obrigatória quando a despesa está paga.")
            if status == "pendente":
                self.data_pagamento = None
            self.vigencia_inicio = None
            self.vigencia_fim = None
        elif rec == "mensal":
            if self.data_vencimento is None:
                raise ValueError("Data de vencimento é obrigatória para custo recorrente (fixo).")
            if self.vigencia_inicio is None:
                self.vigencia_inicio = date.today().replace(day=1)
            self.vigencia_fim = None
        elif rec == "temporaria":
            if self.data_vencimento is None:
                raise ValueError("Data de vencimento é obrigatória para custo temporário.")
            if self.vigencia_inicio is None or self.vigencia_fim is None:
                raise ValueError("Custo temporário exige data de início e fim.")
            if self.vigencia_fim < self.vigencia_inicio:
                raise ValueError("A data fim deve ser maior ou igual à data início.")
        else:
            raise ValueError("Recorrência inválida. Use avulsa, mensal ou temporaria.")
        return self


class DespesaUpdate(BaseModel):
    data_pagamento: date | None = None
    data_vencimento: date | None = None
    descricao: str | None = Field(None, min_length=1, max_length=300)
    categoria_id: int | None = None
    status: str | None = None
    valor: Decimal | None = Field(None, gt=0)
    recorrencia: str | None = None
    vigencia_inicio: date | None = None
    vigencia_fim: date | None = None


class DespesaStatusUpdate(BaseModel):
    status: str  # pago | pendente
    data_pagamento: date | None = None
    mes: str | None = None  # YYYY-MM — obrigatório para recorrentes


class DespesaResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    data_pagamento: date | None = None
    data_vencimento: date | None = None
    descricao: str
    categoria_id: int
    categoria_nome: str | None = None
    status: str
    valor: Decimal
    recorrencia: str = "avulsa"
    vigencia_inicio: date | None = None
    vigencia_fim: date | None = None
    competencia: str | None = None
    ocorrencia_id: int | None = None
    criado_em: UTCDatetime
    atualizado_em: UTCDatetime | None = None


class ResumoCategoriaItem(BaseModel):
    categoria_id: int
    categoria_nome: str
    total: Decimal
    percentual: float


class DespesasResumoResponse(BaseModel):
    mes: str | None = None
    total: Decimal
    total_pago: Decimal
    total_pendente: Decimal
    quantidade: int
    por_categoria: list[ResumoCategoriaItem]


class DespesasPainelResponse(BaseModel):
    """Lista + resumo em uma única resposta (evita 2 round-trips)."""
    despesas: list[DespesaResponse]
    resumo: DespesasResumoResponse


class ImportacaoDespesasResponse(BaseModel):
    inseridas: int
    ignoradas_duplicadas: int
    erros: list[str]
