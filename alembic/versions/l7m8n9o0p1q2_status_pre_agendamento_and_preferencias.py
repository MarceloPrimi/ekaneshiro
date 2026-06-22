"""status_pre_agendamento_and_preferencias

Revision ID: l7m8n9o0p1q2
Revises: j6k7l8m9n0o1
Create Date: 2026-06-22 00:00:00.000000

Alterações:
1. Adiciona valor 'pre_agendamento' ao ENUM de status de agendamento.
2. Migra todos os registros com status='cancelado' para 'pre_agendamento'.
3. Cria a tabela preferencias_usuario para persistência de presets de cores.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'l7m8n9o0p1q2'
down_revision: Union[str, None] = 'j6k7l8m9n0o1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── 1. Adicionar 'pre_agendamento' ao ENUM de status ──────────────────
    # No MySQL, MODIFY COLUMN reescreve o tipo ENUM incluindo o novo valor.
    # Mantemos 'cancelado' para não quebrar dados antigos ainda não migrados.
    op.execute(
        "ALTER TABLE agendamentos MODIFY COLUMN status "
        "ENUM('pendente','confirmado','concluido','cancelado','pre_agendamento') "
        "NOT NULL DEFAULT 'pendente'"
    )

    # ── 2. Migrar dados: cancelado → pre_agendamento ────────────────────────
    op.execute(
        "UPDATE agendamentos SET status = 'pre_agendamento' WHERE status = 'cancelado'"
    )

    # ── 3. Criar tabela preferencias_usuario ────────────────────────────────
    op.create_table(
        "preferencias_usuario",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("preset_cores", sa.JSON(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("usuario_id"),
    )
    op.create_index("ix_preferencias_usuario_usuario_id", "preferencias_usuario", ["usuario_id"])


def downgrade() -> None:
    # ── 3. Remover tabela preferencias_usuario ──────────────────────────────
    op.drop_index("ix_preferencias_usuario_usuario_id", table_name="preferencias_usuario")
    op.drop_table("preferencias_usuario")

    # ── 2. Reverter migração de dados ───────────────────────────────────────
    op.execute(
        "UPDATE agendamentos SET status = 'cancelado' WHERE status = 'pre_agendamento'"
    )

    # ── 1. Reverter ENUM para remover 'pre_agendamento' ────────────────────
    op.execute(
        "ALTER TABLE agendamentos MODIFY COLUMN status "
        "ENUM('pendente','confirmado','concluido','cancelado') "
        "NOT NULL DEFAULT 'pendente'"
    )
