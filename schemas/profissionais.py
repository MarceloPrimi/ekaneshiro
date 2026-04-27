from pydantic import BaseModel

from schemas.servicos import ServicoResponse


class ProfissionalCreate(BaseModel):
    nome: str
    usuario_id: int | None = None
    google_calendar_id: str | None = None


class ProfissionalUpdate(BaseModel):
    nome: str | None = None
    ativo: bool | None = None
    google_calendar_id: str | None = None
    usuario_id: int | None = None  # enviar null = desvincular; omitir = não alterar


class ProfissionalResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    nome: str
    ativo: bool
    usuario_id: int | None
    google_calendar_id: str | None


class ProfissionalComServicosResponse(ProfissionalResponse):
    model_config = {"from_attributes": True}

    servicos: list[ServicoResponse] = []

    @classmethod
    def from_orm_with_servicos(cls, profissional):
        return cls(
            id=profissional.id,
            nome=profissional.nome,
            ativo=profissional.ativo,
            usuario_id=profissional.usuario_id,
            google_calendar_id=profissional.google_calendar_id,
            servicos=[ps.servico for ps in profissional.servicos],
        )
