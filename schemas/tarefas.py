from datetime import datetime

from pydantic import BaseModel

from schemas import UTCDatetime


class TarefaCreate(BaseModel):
    titulo: str
    descricao: str | None = None
    data_hora_inicio: datetime
    data_hora_fim: datetime | None = None
    responsavel_id: int | None = None
    concluida: bool = False


class TarefaUpdate(BaseModel):
    titulo: str | None = None
    descricao: str | None = None
    data_hora_inicio: datetime | None = None
    data_hora_fim: datetime | None = None
    responsavel_id: int | None = None
    concluida: bool | None = None


class UsuarioSimples(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    nome: str


class TarefaResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    titulo: str
    descricao: str | None
    data_hora_inicio: datetime
    data_hora_fim: datetime | None
    responsavel_id: int | None
    responsavel: UsuarioSimples | None
    concluida: bool
    criado_em: UTCDatetime
