from decimal import Decimal

from pydantic import BaseModel

from schemas.servicos import ServicoResponse


class ProfissionalCreate(BaseModel):
    nome: str
    usuario_id: int | None = None
    google_calendar_id: str | None = None
    telefone: str | None = None
    chave_pix: str | None = None


class ProfissionalUpdate(BaseModel):
    nome: str | None = None
    ativo: bool | None = None
    google_calendar_id: str | None = None
    usuario_id: int | None = None  # enviar null = desvincular; omitir = não alterar
    telefone: str | None = None
    chave_pix: str | None = None


class ProfissionalResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    nome: str
    ativo: bool
    usuario_id: int | None
    google_calendar_id: str | None
    telefone: str | None = None
    chave_pix: str | None = None


class ServicoComPrecoResponse(ServicoResponse):
    """Serviço com o preço próprio do profissional (se definido)."""
    preco_proprio: Decimal | None = None


class ProfissionalComServicosResponse(ProfissionalResponse):
    model_config = {"from_attributes": True}

    servicos: list[ServicoComPrecoResponse] = []

    @classmethod
    def from_orm_with_servicos(cls, profissional):
        servicos_com_preco = []
        for ps in profissional.servicos:
            s = ps.servico
            servicos_com_preco.append(
                ServicoComPrecoResponse(
                    id=s.id,
                    nome=s.nome,
                    descricao=s.descricao,
                    duracao_minutos=s.duracao_minutos,
                    preco=s.preco,
                    preco_minimo=s.preco_minimo,
                    preco_maximo=s.preco_maximo,
                    ativo=s.ativo,
                    preco_proprio=ps.preco_proprio,
                )
            )
        return cls(
            id=profissional.id,
            nome=profissional.nome,
            ativo=profissional.ativo,
            usuario_id=profissional.usuario_id,
            google_calendar_id=profissional.google_calendar_id,
            telefone=profissional.telefone,
            chave_pix=profissional.chave_pix,
            servicos=servicos_com_preco,
        )


class ProfissionalServicoPrecoUpdate(BaseModel):
    preco_proprio: Decimal | None = None
