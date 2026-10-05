"""add recorrencia + despesa_ocorrencias for custos fixos/temporarios

Revision ID: p1q2r3s4t5u6
Revises: o0p1q2r3s4t5
Create Date: 2026-10-04
"""

import sqlalchemy as sa
from alembic import op


revision = "p1q2r3s4t5u6"
down_revision = "o0p1q2r3s4t5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "despesas",
        sa.Column(
            "recorrencia",
            sa.Enum("avulsa", "mensal", "temporaria", name="recorrenciadespesaenum"),
            nullable=False,
            server_default="avulsa",
        ),
    )
    op.add_column("despesas", sa.Column("vigencia_inicio", sa.Date(), nullable=True))
    op.add_column("despesas", sa.Column("vigencia_fim", sa.Date(), nullable=True))
    op.create_index("ix_despesas_recorrencia", "despesas", ["recorrencia"])

    op.create_table(
        "despesa_ocorrencias",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "despesa_id",
            sa.Integer,
            sa.ForeignKey("despesas.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("competencia", sa.String(7), nullable=False),  # YYYY-MM
        sa.Column(
            "status",
            sa.Enum("pago", "pendente", name="statusdespesaocorrenciaenum"),
            nullable=False,
            server_default="pendente",
        ),
        sa.Column("data_pagamento", sa.Date(), nullable=True),
        sa.Column(
            "criado_em",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("atualizado_em", sa.DateTime, nullable=True),
        sa.UniqueConstraint("despesa_id", "competencia", name="uq_despesa_competencia"),
    )
    op.create_index("ix_despesa_ocorrencias_despesa_id", "despesa_ocorrencias", ["despesa_id"])
    op.create_index("ix_despesa_ocorrencias_competencia", "despesa_ocorrencias", ["competencia"])

    # Custos Fixos existentes viram mensais e ganham ocorrência no mês do pagamento
    op.execute(
        """
        UPDATE despesas d
        JOIN categorias_despesa c ON c.id = d.categoria_id
        SET d.recorrencia = 'mensal',
            d.vigencia_inicio = COALESCE(d.data_pagamento, DATE(d.criado_em))
        WHERE c.nome = 'Custos Fixos'
        """
    )
    op.execute(
        """
        INSERT INTO despesa_ocorrencias (despesa_id, competencia, status, data_pagamento)
        SELECT
            d.id,
            DATE_FORMAT(COALESCE(d.data_pagamento, d.criado_em), '%Y-%m'),
            d.status,
            d.data_pagamento
        FROM despesas d
        JOIN categorias_despesa c ON c.id = d.categoria_id
        WHERE c.nome = 'Custos Fixos'
        """
    )
    # Template recorrente não guarda pagamento na linha-mãe
    op.execute(
        """
        UPDATE despesas d
        JOIN categorias_despesa c ON c.id = d.categoria_id
        SET d.status = 'pendente', d.data_pagamento = NULL
        WHERE c.nome = 'Custos Fixos'
        """
    )


def downgrade() -> None:
    op.drop_index("ix_despesa_ocorrencias_competencia", table_name="despesa_ocorrencias")
    op.drop_index("ix_despesa_ocorrencias_despesa_id", table_name="despesa_ocorrencias")
    op.drop_table("despesa_ocorrencias")
    op.drop_index("ix_despesas_recorrencia", table_name="despesas")
    op.drop_column("despesas", "vigencia_fim")
    op.drop_column("despesas", "vigencia_inicio")
    op.drop_column("despesas", "recorrencia")
    sa.Enum(name="statusdespesaocorrenciaenum").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="recorrenciadespesaenum").drop(op.get_bind(), checkfirst=True)
