"""melhorias_v2: range precos servico, preco proprio profissional, obs e campos dinamicos cliente

Revision ID: a1b2c3d4e5f6
Revises: d8f7b2536e5d
Create Date: 2026-05-03 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'd8f7b2536e5d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- servicos: range de preços ---
    op.add_column('servicos', sa.Column('preco_minimo', sa.Numeric(10, 2), nullable=True))
    op.add_column('servicos', sa.Column('preco_maximo', sa.Numeric(10, 2), nullable=True))

    # --- profissionais_servicos: preço próprio do profissional ---
    op.add_column(
        'profissionais_servicos',
        sa.Column('preco_proprio', sa.Numeric(10, 2), nullable=True),
    )

    # --- clientes: observações e campos dinâmicos ---
    op.add_column('clientes', sa.Column('observacoes', sa.Text(), nullable=True))
    op.add_column('clientes', sa.Column('campos_dinamicos', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('clientes', 'campos_dinamicos')
    op.drop_column('clientes', 'observacoes')
    op.drop_column('profissionais_servicos', 'preco_proprio')
    op.drop_column('servicos', 'preco_maximo')
    op.drop_column('servicos', 'preco_minimo')
