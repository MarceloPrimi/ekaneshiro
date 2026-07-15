"""add comandas: Comanda, ItemComanda, PagamentoComanda

Revision ID: m8n9o0p1q2r3
Revises: l7m8n9o0p1q2
Create Date: 2026-07-14 00:00:00.000000

Introduz o sistema de comanda (caixa tipo padaria) com três novas tabelas:
  - comandas          : cabeçalho da comanda (status, timestamps, operador)
  - itens_comanda     : linhas de serviço/produto com profissional e valor congelado
  - pagamentos_comanda: registros de pagamento (suporta split por método/pagador)
"""

import sqlalchemy as sa
from alembic import op


revision = "m8n9o0p1q2r3"
down_revision = "l7m8n9o0p1q2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # 1. comandas
    # ------------------------------------------------------------------
    op.create_table(
        "comandas",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "status",
            sa.Enum("aberta", "fechada", "cancelada", name="statuscomandaenum"),
            nullable=False,
            server_default="aberta",
        ),
        sa.Column("observacoes", sa.Text, nullable=True),
        sa.Column(
            "aberta_em",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("fechada_em", sa.DateTime, nullable=True),
        sa.Column("criada_por_id", sa.Integer, sa.ForeignKey("usuarios.id"), nullable=True),
    )
    op.create_index("ix_comandas_id", "comandas", ["id"])
    op.create_index("ix_comandas_status", "comandas", ["status"])
    op.create_index("ix_comandas_aberta_em", "comandas", ["aberta_em"])

    # ------------------------------------------------------------------
    # 2. itens_comanda
    # ------------------------------------------------------------------
    op.create_table(
        "itens_comanda",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "comanda_id",
            sa.Integer,
            sa.ForeignKey("comandas.id"),
            nullable=False,
        ),
        sa.Column(
            "tipo",
            sa.Enum(
                "agendamento", "servico_avulso", "produto",
                name="tipoitemcomandaenum",
            ),
            nullable=False,
        ),
        sa.Column(
            "agendamento_id",
            sa.Integer,
            sa.ForeignKey("agendamentos.id"),
            nullable=True,
        ),
        sa.Column(
            "item_agendamento_id",
            sa.Integer,
            sa.ForeignKey("itens_agendamento.id"),
            nullable=True,
            unique=True,
        ),
        sa.Column(
            "cliente_id",
            sa.Integer,
            sa.ForeignKey("clientes.id"),
            nullable=False,
        ),
        sa.Column(
            "profissional_id",
            sa.Integer,
            sa.ForeignKey("profissionais.id"),
            nullable=True,
        ),
        sa.Column(
            "servico_id",
            sa.Integer,
            sa.ForeignKey("servicos.id"),
            nullable=True,
        ),
        sa.Column("descricao", sa.String(300), nullable=True),
        sa.Column("valor_unitario", sa.Numeric(10, 2), nullable=False),
        sa.Column("quantidade", sa.Integer, nullable=False, server_default="1"),
        sa.Column("desconto", sa.Numeric(10, 2), nullable=False, server_default="0.00"),
    )
    op.create_index("ix_itens_comanda_id", "itens_comanda", ["id"])
    op.create_index("ix_itens_comanda_comanda_id", "itens_comanda", ["comanda_id"])
    op.create_index("ix_itens_comanda_agendamento_id", "itens_comanda", ["agendamento_id"])
    op.create_index("ix_itens_comanda_cliente_id", "itens_comanda", ["cliente_id"])
    op.create_index("ix_itens_comanda_profissional_id", "itens_comanda", ["profissional_id"])

    # ------------------------------------------------------------------
    # 3. pagamentos_comanda
    # ------------------------------------------------------------------
    op.create_table(
        "pagamentos_comanda",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "comanda_id",
            sa.Integer,
            sa.ForeignKey("comandas.id"),
            nullable=False,
        ),
        sa.Column("valor", sa.Numeric(10, 2), nullable=False),
        sa.Column("metodo", sa.String(50), nullable=False),
        sa.Column(
            "credito_utilizado",
            sa.Numeric(10, 2),
            nullable=False,
            server_default="0.00",
        ),
        sa.Column(
            "pagador_cliente_id",
            sa.Integer,
            sa.ForeignKey("clientes.id"),
            nullable=True,
        ),
        sa.Column(
            "pago_em",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "registrado_por_id",
            sa.Integer,
            sa.ForeignKey("usuarios.id"),
            nullable=True,
        ),
    )
    op.create_index("ix_pagamentos_comanda_id", "pagamentos_comanda", ["id"])
    op.create_index("ix_pagamentos_comanda_comanda_id", "pagamentos_comanda", ["comanda_id"])


def downgrade() -> None:
    op.drop_index("ix_pagamentos_comanda_comanda_id", "pagamentos_comanda")
    op.drop_index("ix_pagamentos_comanda_id", "pagamentos_comanda")
    op.drop_table("pagamentos_comanda")

    op.drop_index("ix_itens_comanda_profissional_id", "itens_comanda")
    op.drop_index("ix_itens_comanda_cliente_id", "itens_comanda")
    op.drop_index("ix_itens_comanda_agendamento_id", "itens_comanda")
    op.drop_index("ix_itens_comanda_comanda_id", "itens_comanda")
    op.drop_index("ix_itens_comanda_id", "itens_comanda")
    op.drop_table("itens_comanda")

    op.drop_index("ix_comandas_aberta_em", "comandas")
    op.drop_index("ix_comandas_status", "comandas")
    op.drop_index("ix_comandas_id", "comandas")
    op.drop_table("comandas")

    # Remove os ENUMs criados (necessário em PostgreSQL; no-op no SQLite)
    sa.Enum(name="tipoitemcomandaenum").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="statuscomandaenum").drop(op.get_bind(), checkfirst=True)
