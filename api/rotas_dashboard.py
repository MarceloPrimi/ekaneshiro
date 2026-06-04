"""Endpoint BFF (Backend For Frontend) para carga inicial do dashboard.

Substitui 6–8 requests paralelas por uma única chamada, eliminando o
blocked/queued time de 180–480ms por request que o browser impõe ao
compartilhar conexões HTTP com o mesmo host.

Ganho estimado: -2 a -3 segundos no tempo de carga inicial.
"""
from datetime import date, datetime, time, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload, selectinload

from api.dependencias import get_current_user
from db.database import get_db
from db.models import (
    Agendamento,
    ItemAgendamento,
    Profissional,
    ProfissionalSecao,
    ProfissionalServico,
    Servico,
    TarefaInterna,
    Usuario,
)
from schemas.agendamentos import AgendamentoResponse
from schemas.profissionais import ProfissionalComServicosResponse
from schemas.servicos import ServicoResponse
from schemas.tarefas import TarefaResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

_EAGER_AGENDAMENTO = [
    joinedload(Agendamento.cliente),
    selectinload(Agendamento.itens).options(
        joinedload(ItemAgendamento.servico),
        joinedload(ItemAgendamento.profissional),
    ),
    joinedload(Agendamento.pagamento),
]

_EAGER_PROFISSIONAL = [
    selectinload(Profissional.servicos).joinedload(ProfissionalServico.servico),
    selectinload(Profissional.secoes).joinedload(ProfissionalSecao.secao),
]


@router.get("/init", summary="Carga inicial do calendário em uma única chamada")
def dashboard_init(
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """Agrega servicos + profissionais + agendamentos da semana + tarefas em 1 request.

    A janela de agendamentos retornada aqui é a semana atual ±10 dias (mínimo para
    pintar o calendário inicial). O frontend amplia progressivamente em background.
    """
    hoje = date.today()
    inicio = datetime.combine(hoje - timedelta(days=10), time.min)
    fim = datetime.combine(hoje + timedelta(days=10), time.max)

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

    # Profissional só vê os próprios agendamentos
    from db.models import RoleEnum
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

    tarefas = (
        db.query(TarefaInterna)
        .order_by(TarefaInterna.data_hora_inicio)
        .all()
    )

    return {
        "servicos": [ServicoResponse.model_validate(s) for s in servicos],
        "profissionais": [
            ProfissionalComServicosResponse.from_orm_with_servicos(p)
            for p in profissionais
        ],
        "agendamentos": [AgendamentoResponse.model_validate(ag) for ag in agendamentos],
        "tarefas": [TarefaResponse.model_validate(t) for t in tarefas],
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
