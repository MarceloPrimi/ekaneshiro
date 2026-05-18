"""initial_schema

Revision ID: 90255258a610
Revises: 
Create Date: 2026-04-24 15:31:13.893451

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '90255258a610'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('usuarios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=150), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('admin', 'recepcionista', 'profissional', name='roleenum'), nullable=False),
        sa.Column('ativo', sa.Boolean(), nullable=False),
        sa.Column('criado_em', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_usuarios_id'), 'usuarios', ['id'], unique=False)
    op.create_index(op.f('ix_usuarios_email'), 'usuarios', ['email'], unique=True)

    op.create_table('clientes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('telefone', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=150), nullable=True),
        sa.Column('criado_em', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_clientes_id'), 'clientes', ['id'], unique=False)
    op.create_index(op.f('ix_clientes_email'), 'clientes', ['email'], unique=False)

    op.create_table('profissionais',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('ativo', sa.Boolean(), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=True),
        sa.Column('google_calendar_id', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('usuario_id'),
    )
    op.create_index(op.f('ix_profissionais_id'), 'profissionais', ['id'], unique=False)

    op.create_table('servicos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('duracao_minutos', sa.Integer(), nullable=False),
        sa.Column('preco', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('ativo', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_servicos_id'), 'servicos', ['id'], unique=False)

    op.create_table('profissionais_servicos',
        sa.Column('profissional_id', sa.Integer(), nullable=False),
        sa.Column('servico_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['profissional_id'], ['profissionais.id']),
        sa.ForeignKeyConstraint(['servico_id'], ['servicos.id']),
        sa.PrimaryKeyConstraint('profissional_id', 'servico_id'),
    )

    op.create_table('agendamentos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cliente_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('pendente', 'confirmado', 'concluido', 'cancelado', name='statusagendamentoenum'), nullable=False),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('criado_em', sa.DateTime(), nullable=False),
        sa.Column('criado_por_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['cliente_id'], ['clientes.id']),
        sa.ForeignKeyConstraint(['criado_por_id'], ['usuarios.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_agendamentos_id'), 'agendamentos', ['id'], unique=False)

    op.create_table('itens_agendamento',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('agendamento_id', sa.Integer(), nullable=False),
        sa.Column('servico_id', sa.Integer(), nullable=False),
        sa.Column('profissional_id', sa.Integer(), nullable=False),
        sa.Column('data_hora_inicio', sa.DateTime(), nullable=False),
        sa.Column('data_hora_fim', sa.DateTime(), nullable=False),
        sa.Column('google_event_id', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['agendamento_id'], ['agendamentos.id']),
        sa.ForeignKeyConstraint(['servico_id'], ['servicos.id']),
        sa.ForeignKeyConstraint(['profissional_id'], ['profissionais.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_itens_agendamento_id'), 'itens_agendamento', ['id'], unique=False)
    op.create_index(op.f('ix_itens_agendamento_data_hora_inicio'), 'itens_agendamento', ['data_hora_inicio'], unique=False)

    op.create_table('pagamentos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('agendamento_id', sa.Integer(), nullable=False),
        sa.Column('valor', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('metodo', sa.String(length=50), nullable=False),
        sa.Column('pago_em', sa.DateTime(), nullable=False),
        sa.Column('registrado_por_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['agendamento_id'], ['agendamentos.id']),
        sa.ForeignKeyConstraint(['registrado_por_id'], ['usuarios.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('agendamento_id'),
    )
    op.create_index(op.f('ix_pagamentos_id'), 'pagamentos', ['id'], unique=False)

    op.create_table('google_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('account_label', sa.String(length=100), nullable=False),
        sa.Column('access_token', sa.Text(), nullable=False),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('token_expiry', sa.DateTime(), nullable=True),
        sa.Column('atualizado_em', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('account_label'),
    )
    op.create_index(op.f('ix_google_tokens_id'), 'google_tokens', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_google_tokens_id'), table_name='google_tokens')
    op.drop_table('google_tokens')
    op.drop_index(op.f('ix_pagamentos_id'), table_name='pagamentos')
    op.drop_table('pagamentos')
    op.drop_index(op.f('ix_itens_agendamento_data_hora_inicio'), table_name='itens_agendamento')
    op.drop_index(op.f('ix_itens_agendamento_id'), table_name='itens_agendamento')
    op.drop_table('itens_agendamento')
    op.drop_index(op.f('ix_agendamentos_id'), table_name='agendamentos')
    op.drop_table('agendamentos')
    op.drop_table('profissionais_servicos')
    op.drop_index(op.f('ix_servicos_id'), table_name='servicos')
    op.drop_table('servicos')
    op.drop_index(op.f('ix_profissionais_id'), table_name='profissionais')
    op.drop_table('profissionais')
    op.drop_index(op.f('ix_clientes_email'), table_name='clientes')
    op.drop_index(op.f('ix_clientes_id'), table_name='clientes')
    op.drop_table('clientes')
    op.drop_index(op.f('ix_usuarios_email'), table_name='usuarios')
    op.drop_index(op.f('ix_usuarios_id'), table_name='usuarios')
    op.drop_table('usuarios')
    op.drop_index(op.f('ix_itens_agendamento_data_hora_inicio'), table_name='itens_agendamento')
    op.drop_index(op.f('ix_google_tokens_id'), table_name='google_tokens')
    op.drop_index(op.f('ix_clientes_id'), table_name='clientes')
    op.drop_index(op.f('ix_clientes_email'), table_name='clientes')
    op.drop_index(op.f('ix_agendamentos_id'), table_name='agendamentos')
    # ### end Alembic commands ###
