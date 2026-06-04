"""add_feriados_table

Revision ID: j6k7l8m9n0o1
Revises: i4j5k6l7m8n9
Create Date: 2026-06-04 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'j6k7l8m9n0o1'
down_revision: Union[str, None] = 'i4j5k6l7m8n9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'feriados',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('data', sa.String(length=10), nullable=False),
        sa.Column('nome', sa.String(length=200), nullable=False),
        sa.Column('bloquear_agenda', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('criado_em', sa.DateTime(), nullable=False),
        sa.Column('criado_por_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['criado_por_id'], ['usuarios.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('data'),
    )
    op.create_index(op.f('ix_feriados_id'), 'feriados', ['id'], unique=False)
    op.create_index(op.f('ix_feriados_data'), 'feriados', ['data'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_feriados_data'), table_name='feriados')
    op.drop_index(op.f('ix_feriados_id'), table_name='feriados')
    op.drop_table('feriados')
