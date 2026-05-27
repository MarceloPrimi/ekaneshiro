"""add_secoes: tabela de secoes, secao_id em servicos, profissionais_secoes

Revision ID: g1h2i3j4k5l6
Revises: e1f2a3b4c5d6
Create Date: 2026-05-30 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'g1h2i3j4k5l6'
down_revision = 'e1f2a3b4c5d6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Tabela de seções
    op.create_table(
        'secoes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(100), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nome'),
    )
    op.create_index(op.f('ix_secoes_id'), 'secoes', ['id'], unique=False)

    # FK em servicos
    op.add_column('servicos', sa.Column('secao_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_servicos_secao_id', 'servicos', 'secoes', ['secao_id'], ['id'])
    op.create_index('ix_servicos_secao_id', 'servicos', ['secao_id'], unique=False)

    # Tabela N:N profissionais <-> secoes
    op.create_table(
        'profissionais_secoes',
        sa.Column('profissional_id', sa.Integer(), nullable=False),
        sa.Column('secao_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['profissional_id'], ['profissionais.id']),
        sa.ForeignKeyConstraint(['secao_id'], ['secoes.id']),
        sa.PrimaryKeyConstraint('profissional_id', 'secao_id'),
    )


def downgrade() -> None:
    op.drop_table('profissionais_secoes')
    op.drop_index('ix_servicos_secao_id', table_name='servicos')
    op.drop_constraint('fk_servicos_secao_id', 'servicos', type_='foreignkey')
    op.drop_column('servicos', 'secao_id')
    op.drop_index(op.f('ix_secoes_id'), table_name='secoes')
    op.drop_table('secoes')
