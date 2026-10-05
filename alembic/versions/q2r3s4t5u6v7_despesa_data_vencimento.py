"""add data_vencimento to despesas (required for custos recorrentes)

Revision ID: q2r3s4t5u6v7
Revises: p1q2r3s4t5u6
Create Date: 2026-10-04
"""

import sqlalchemy as sa
from alembic import op


revision = "q2r3s4t5u6v7"
down_revision = "p1q2r3s4t5u6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("despesas", sa.Column("data_vencimento", sa.Date(), nullable=True))
    op.create_index("ix_despesas_data_vencimento", "despesas", ["data_vencimento"])

    # Backfill: recorrentes usam vigência/pagamento/criação como vencimento inicial
    op.execute(
        """
        UPDATE despesas
        SET data_vencimento = COALESCE(data_pagamento, vigencia_inicio, DATE(criado_em))
        WHERE recorrencia IN ('mensal', 'temporaria')
          AND data_vencimento IS NULL
        """
    )


def downgrade() -> None:
    op.drop_index("ix_despesas_data_vencimento", table_name="despesas")
    op.drop_column("despesas", "data_vencimento")
