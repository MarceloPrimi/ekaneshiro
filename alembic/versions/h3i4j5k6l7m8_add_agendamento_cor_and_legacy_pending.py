"""add agendamento cor and force legacy status pending

Revision ID: h3i4j5k6l7m8
Revises: g1h2i3j4k5l6
Create Date: 2026-05-27 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "h3i4j5k6l7m8"
down_revision = "g1h2i3j4k5l6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("agendamentos", sa.Column("cor_hex", sa.String(length=7), nullable=True))
    # Registros legados (importados sem criador) devem permanecer pendentes.
    op.execute("UPDATE agendamentos SET status = 'pendente' WHERE criado_por_id IS NULL")


def downgrade() -> None:
    op.drop_column("agendamentos", "cor_hex")
