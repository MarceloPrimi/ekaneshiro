"""add cor_card to clientes

Revision ID: add_cor_card_cliente
Revises: m8n9o0p1q2r3
Create Date: 2026-07-28

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_cor_card_cliente'
down_revision = 'm8n9o0p1q2r3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('clientes', sa.Column('cor_card', sa.String(7), nullable=True))


def downgrade() -> None:
    op.drop_column('clientes', 'cor_card')
