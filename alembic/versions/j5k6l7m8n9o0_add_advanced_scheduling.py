"""add advanced scheduling: categories, recurrence, mini_etiquetas, primeira_vez

Revision ID: j5k6l7m8n9o0
Revises: i4j5k6l7m8n9
Create Date: 2026-05-31 00:00:00.000000
"""

import sqlalchemy as sa
from alembic import op


revision = "j5k6l7m8n9o0"
down_revision = "0b30d888200d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # 1. Tabela: categorias_agendamento
    # ------------------------------------------------------------------
    op.create_table(
        "categorias_agendamento",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("nome", sa.String(100), nullable=False),
        sa.Column("cor_hex", sa.String(7), nullable=False, server_default="#6366f1"),
        sa.Column("ativo", sa.Boolean, nullable=False, server_default="1"),
        sa.Column(
            "criado_em", sa.DateTime, nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index(
        "ix_categorias_agendamento_nome",
        "categorias_agendamento",
        ["nome"],
        unique=True,
    )

    # ------------------------------------------------------------------
    # 2. Novas colunas em agendamentos
    # ------------------------------------------------------------------

    # Categoria de cor/tipo
    op.add_column(
        "agendamentos",
        sa.Column(
            "categoria_id",
            sa.Integer,
            sa.ForeignKey("categorias_agendamento.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_agendamentos_categoria_id", "agendamentos", ["categoria_id"]
    )

    # Recorrência: regra RRULE e FK para o agendamento-pai da série
    op.add_column(
        "agendamentos",
        sa.Column("recurrence_rule", sa.String(500), nullable=True),
    )
    op.add_column(
        "agendamentos",
        sa.Column(
            "parent_id",
            sa.Integer,
            sa.ForeignKey("agendamentos.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_agendamentos_parent_id", "agendamentos", ["parent_id"]
    )

    # Mini etiquetas (JSON array de strings, ex: ["urgente","pago"])
    op.add_column(
        "agendamentos",
        sa.Column("mini_etiquetas", sa.JSON, nullable=True),
    )

    # Flag calculada: se este agendamento é a 1ª vez do cliente
    op.add_column(
        "agendamentos",
        sa.Column(
            "primeira_vez",
            sa.Boolean,
            nullable=False,
            server_default="0",
        ),
    )


def downgrade() -> None:
    op.drop_index("ix_agendamentos_parent_id", "agendamentos")
    op.drop_column("agendamentos", "parent_id")
    op.drop_column("agendamentos", "recurrence_rule")
    op.drop_index("ix_agendamentos_categoria_id", "agendamentos")
    op.drop_column("agendamentos", "categoria_id")
    op.drop_column("agendamentos", "mini_etiquetas")
    op.drop_column("agendamentos", "primeira_vez")

    op.drop_index("ix_categorias_agendamento_nome", "categorias_agendamento")
    op.drop_table("categorias_agendamento")
