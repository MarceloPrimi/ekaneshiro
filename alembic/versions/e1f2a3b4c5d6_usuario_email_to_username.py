"""usuario_email_to_username: substitui coluna email por username no login

Revision ID: e1f2a3b4c5d6
Revises: c1d2e3f4a5b6
Create Date: 2026-05-27 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e1f2a3b4c5d6'
down_revision: Union[str, None] = 'c1d2e3f4a5b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Adiciona coluna username (nullable para popular antes de tornar obrigatória)
    op.add_column('usuarios', sa.Column('username', sa.String(length=150), nullable=True))

    # 2. Popula com o valor atual de email (mantém compatibilidade)
    op.execute("UPDATE usuarios SET username = email")

    # 3. Torna NOT NULL após popular
    op.alter_column('usuarios', 'username', existing_type=sa.String(length=150), nullable=False)

    # 4. Cria índice único para username
    op.create_index('ix_usuarios_username', 'usuarios', ['username'], unique=True)

    # 5. Remove índice e coluna de email
    op.drop_index('ix_usuarios_email', table_name='usuarios')
    op.drop_column('usuarios', 'email')


def downgrade() -> None:
    op.add_column('usuarios', sa.Column('email', sa.String(length=150), nullable=True))
    op.execute("UPDATE usuarios SET email = username")
    op.alter_column('usuarios', 'email', existing_type=sa.String(length=150), nullable=False)
    op.create_index('ix_usuarios_email', 'usuarios', ['email'], unique=True)
    op.drop_index('ix_usuarios_username', table_name='usuarios')
    op.drop_column('usuarios', 'username')
