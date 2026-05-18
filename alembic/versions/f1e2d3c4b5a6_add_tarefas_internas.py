"""add_tarefas_internas

Revision ID: f1e2d3c4b5a6
Revises: a1b2c3d4e5f6
Create Date: 2026-05-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f1e2d3c4b5a6'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'tarefas_internas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('titulo', sa.String(length=200), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('data_hora_inicio', sa.DateTime(), nullable=False),
        sa.Column('data_hora_fim', sa.DateTime(), nullable=True),
        sa.Column('responsavel_id', sa.Integer(), nullable=True),
        sa.Column('criado_por_id', sa.Integer(), nullable=True),
        sa.Column('concluida', sa.Boolean(), nullable=False),
        sa.Column('criado_em', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['criado_por_id'], ['usuarios.id']),
        sa.ForeignKeyConstraint(['responsavel_id'], ['usuarios.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_tarefas_internas_id'), 'tarefas_internas', ['id'], unique=False
    )
    op.create_index(
        op.f('ix_tarefas_internas_data_hora_inicio'),
        'tarefas_internas',
        ['data_hora_inicio'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_tarefas_internas_data_hora_inicio'), table_name='tarefas_internas')
    op.drop_index(op.f('ix_tarefas_internas_id'), table_name='tarefas_internas')
    op.drop_table('tarefas_internas')
