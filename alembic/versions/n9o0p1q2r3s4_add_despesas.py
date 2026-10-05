"""add categorias_despesa and despesas

Revision ID: n9o0p1q2r3s4
Revises: add_cor_card_cliente
Create Date: 2026-10-04

Introduz o módulo Financeiro — Controle de Despesas:
  - categorias_despesa : catálogo de tipos (seed das categorias da planilha)
  - despesas           : lançamentos com status pago/pendente
"""

import sqlalchemy as sa
from alembic import op


revision = "n9o0p1q2r3s4"
down_revision = "add_cor_card_cliente"
branch_labels = None
depends_on = None

_CATEGORIAS_SEED = [
    "Custos Fixos",
    "Insumos e Produtos",
    "Manutenção e Equipamentos",
    "Marketing e Divulgação",
    "Materiais de Descarte / Higiene",
    "Mão de Obra e Equipe",
    "Serviços Terceirizados",
]


def upgrade() -> None:
    op.create_table(
        "categorias_despesa",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("nome", sa.String(100), nullable=False, unique=True),
        sa.Column("ativo", sa.Boolean, nullable=False, server_default=sa.text("1")),
        sa.Column(
            "criado_em",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index("ix_categorias_despesa_id", "categorias_despesa", ["id"])

    op.create_table(
        "despesas",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("data", sa.Date, nullable=False),
        sa.Column("descricao", sa.String(300), nullable=False),
        sa.Column(
            "categoria_id",
            sa.Integer,
            sa.ForeignKey("categorias_despesa.id"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("pago", "pendente", name="statusdespesaenum"),
            nullable=False,
            server_default="pendente",
        ),
        sa.Column("valor", sa.Numeric(10, 2), nullable=False),
        sa.Column("import_hash", sa.String(64), nullable=True, unique=True),
        sa.Column("criado_por_id", sa.Integer, sa.ForeignKey("usuarios.id"), nullable=True),
        sa.Column(
            "criado_em",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("atualizado_em", sa.DateTime, nullable=True),
    )
    op.create_index("ix_despesas_id", "despesas", ["id"])
    op.create_index("ix_despesas_data", "despesas", ["data"])
    op.create_index("ix_despesas_categoria_id", "despesas", ["categoria_id"])
    op.create_index("ix_despesas_status", "despesas", ["status"])
    op.create_index("ix_despesas_import_hash", "despesas", ["import_hash"])
    op.create_index("ix_despesas_data_status", "despesas", ["data", "status"])

    categorias = sa.table(
        "categorias_despesa",
        sa.column("nome", sa.String),
        sa.column("ativo", sa.Boolean),
    )
    op.bulk_insert(
        categorias,
        [{"nome": nome, "ativo": True} for nome in _CATEGORIAS_SEED],
    )


def downgrade() -> None:
    op.drop_index("ix_despesas_data_status", table_name="despesas")
    op.drop_index("ix_despesas_import_hash", table_name="despesas")
    op.drop_index("ix_despesas_status", table_name="despesas")
    op.drop_index("ix_despesas_categoria_id", table_name="despesas")
    op.drop_index("ix_despesas_data", table_name="despesas")
    op.drop_index("ix_despesas_id", table_name="despesas")
    op.drop_table("despesas")

    op.drop_index("ix_categorias_despesa_id", table_name="categorias_despesa")
    op.drop_table("categorias_despesa")

    sa.Enum(name="statusdespesaenum").drop(op.get_bind(), checkfirst=True)
