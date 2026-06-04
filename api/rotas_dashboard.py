"""Endpoint BFF (Backend For Frontend) para carga inicial do dashboard.

Substitui 6–8 requests paralelas por uma única chamada, eliminando o
blocked/queued time de 180–480ms por request que o browser impõe ao
compartilhar conexões HTTP com o mesmo host.

Ganho estimado: -2 a -3 segundos no tempo de carga inicial.
"""
from datetime import date, datetime, time, timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload, selectinload

from api.dependencias import get_current_user
from db.database import get_db
from db.models import (
    Agendamento,
    ItemAgendamento,
    Profissional,
    ProfissionalSecao,
    ProfissionalServico,
    RoleEnum,
    Servico,
    TarefaInterna,
    Usuario,
)
from schemas.agendamentos import AgendamentoResponse
from schemas.profissionais import ProfissionalComServicosResponse
from schemas.servicos import ServicoResponse
from schemas.tarefas import TarefaResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# Carrega todos os relacionamentos necessários para AgendamentoResponse.
# Inclui 'categoria' para evitar lazy-load que pode causar erro fora do contexto.
_EAGER_AGENDAMENTO = [
    joinedload(Agendamento.cliente),
    selectinload(Agendamento.itens).options(
        joinedload(ItemAgendamento.servico),
        joinedload(ItemAgendamento.profissional),
    ),
    joinedload(Agendamento.pagamento),
    joinedload(Agendamento.categoria),
]

_EAGER_PROFISSIONAL = [
    selectinload(Profissional.servicos).joinedload(ProfissionalServico.servico),
    selectinload(Profissional.secoes).joinedload(ProfissionalSecao.secao),
]


class DashboardInitResponse(BaseModel):
    """Resposta tipada garante serialização correta pelo FastAPI."""
    model_config = {"from_attributes": True}

    servicos: list[ServicoResponse]
    profissionais: list[Any]  # ProfissionalComServicosResponse (construído manualmente)
    agendamentos: list[AgendamentoResponse]
    tarefas: list[TarefaResponse]
    janela_inicio: str   # YYYY-MM-DD — informar o frontend qual janela foi retornada
    janela_fim: str


@router.get(
    "/init",
    summary="Carga inicial do calendário em uma única chamada",
)
def dashboard_init(
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """Agrega servicos + profissionais + agendamentos da semana + tarefas em 1 request.

    Janela de agendamentos: semana atual (hoje-7 a hoje+14 = ~3 semanas).
    O frontend expande sob demanda via onDatesSet (2 semanas por navegação).
    """
    hoje = date.today()
    inicio = datetime.combine(hoje - timedelta(days=7), time.min)
    fim = datetime.combine(hoje + timedelta(days=14), time.max)

    servicos = (
        db.query(Servico)
        .filter(Servico.ativo == True)
        .order_by(Servico.nome)
        .all()
    )

    profissionais = (
        db.query(Profissional)
        .options(*_EAGER_PROFISSIONAL)
        .filter(Profissional.ativo == True)
        .all()
    )

    agendamentos_query = (
        db.query(Agendamento)
        .options(*_EAGER_AGENDAMENTO)
        .filter(
            Agendamento.id.in_(
                db.query(ItemAgendamento.agendamento_id)
                .filter(
                    ItemAgendamento.data_hora_inicio >= inicio,
                    ItemAgendamento.data_hora_inicio <= fim,
                )
                .distinct()
            )
        )
        .order_by(Agendamento.criado_em.desc())
    )

    if current_user.role == RoleEnum.profissional:
        if current_user.profissional:
            agendamentos_query = agendamentos_query.filter(
                Agendamento.id.in_(
                    db.query(ItemAgendamento.agendamento_id)
                    .filter(ItemAgendamento.profissional_id == current_user.profissional.id)
                    .distinct()
                )
            )
        else:
            agendamentos_query = agendamentos_query.filter(False)

    agendamentos = agendamentos_query.all()

    # Eager-load responsavel para evitar N+1 / lazy-load fora de sessão
    tarefas = (
        db.query(TarefaInterna)
        .options(joinedload(TarefaInterna.responsavel))
        .order_by(TarefaInterna.data_hora_inicio)
        .all()
    )

    return {
        "servicos": [ServicoResponse.model_validate(s) for s in servicos],
        "profissionais": [
            ProfissionalComServicosResponse.from_orm_with_servicos(p).model_dump()
            for p in profissionais
        ],
        "agendamentos": [AgendamentoResponse.model_validate(ag).model_dump() for ag in agendamentos],
        "tarefas": [TarefaResponse.model_validate(t).model_dump() for t in tarefas],
        "janela_inicio": str(hoje - timedelta(days=7)),
        "janela_fim": str(hoje + timedelta(days=14)),
    }


@router.get(
    "/profissionais-summary",
    summary="Lista resumida de profissionais (sem serviços embedded)",
)
def profissionais_summary(
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """Retorna apenas id + nome + ativo. 
    
    Use em dropdowns e filtros onde não é necessário carregar a lista completa
    de serviços por profissional (8.4 KB → ~400 bytes).
    """
    rows = (
        db.query(Profissional.id, Profissional.nome, Profissional.ativo)
        .filter(Profissional.ativo == True)
        .order_by(Profissional.nome)
        .all()
    )
    return [{"id": r.id, "nome": r.nome, "ativo": r.ativo} for r in rows]
