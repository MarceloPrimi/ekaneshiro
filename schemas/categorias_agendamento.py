from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Entrada
# ---------------------------------------------------------------------------

class CategoriaAgendamentoCreate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    cor_hex: str = Field("#6366f1", pattern=r"^#[0-9a-fA-F]{6}$")


class CategoriaAgendamentoUpdate(BaseModel):
    nome: str | None = Field(None, min_length=1, max_length=100)
    cor_hex: str | None = Field(None, pattern=r"^#[0-9a-fA-F]{6}$")
    ativo: bool | None = None


# ---------------------------------------------------------------------------
# Saída
# ---------------------------------------------------------------------------

class CategoriaAgendamentoResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    nome: str
    cor_hex: str
    ativo: bool
