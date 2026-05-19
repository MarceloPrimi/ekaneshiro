"""add_performance_indexes

Revision ID: c1d2e3f4a5b6
Revises: f1e2d3c4b5a6
Create Date: 2026-05-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = 'c1d2e3f4a5b6'
down_revision: Union[str, None] = 'f1e2d3c4b5a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Agendamentos: filtros mais comuns
    op.create_index('ix_agendamentos_cliente_id', 'agendamentos', ['cliente_id'], unique=False)
    op.create_index('ix_agendamentos_status', 'agendamentos', ['status'], unique=False)
    op.create_index('ix_agendamentos_criado_em', 'agendamentos', ['criado_em'], unique=False)

    # Itens: busca por profissional e por agendamento pai
    op.create_index('ix_itens_agendamento_profissional_id', 'itens_agendamento', ['profissional_id'], unique=False)
    op.create_index('ix_itens_agendamento_agendamento_id', 'itens_agendamento', ['agendamento_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_itens_agendamento_agendamento_id', table_name='itens_agendamento')
    op.drop_index('ix_itens_agendamento_profissional_id', table_name='itens_agendamento')
    op.drop_index('ix_agendamentos_criado_em', table_name='agendamentos')
    op.drop_index('ix_agendamentos_status', table_name='agendamentos')
    op.drop_index('ix_agendamentos_cliente_id', table_name='agendamentos')
