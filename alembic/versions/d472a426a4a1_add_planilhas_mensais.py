"""add_planilhas_mensais

Revision ID: d472a426a4a1
Revises: 90255258a610
Create Date: 2026-04-24 15:46:10.150943

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd472a426a4a1'
down_revision: Union[str, None] = '90255258a610'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('planilhas_mensais',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('mes', sa.String(length=7), nullable=False),
    sa.Column('spreadsheet_id', sa.String(length=255), nullable=False),
    sa.Column('spreadsheet_url', sa.String(length=500), nullable=False),
    sa.Column('criado_em', sa.DateTime(), nullable=False),
    sa.Column('ultima_exportacao', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_planilhas_mensais_id'), 'planilhas_mensais', ['id'], unique=False)
    op.create_index(op.f('ix_planilhas_mensais_mes'), 'planilhas_mensais', ['mes'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_planilhas_mensais_mes'), table_name='planilhas_mensais')
    op.drop_index(op.f('ix_planilhas_mensais_id'), table_name='planilhas_mensais')
    op.drop_table('planilhas_mensais')
    op.drop_index(op.f('ix_itens_agendamento_id'), table_name='itens_agendamento')
    op.drop_index(op.f('ix_itens_agendamento_data_hora_inicio'), table_name='itens_agendamento')
    op.drop_index(op.f('ix_google_tokens_id'), table_name='google_tokens')
    op.drop_index(op.f('ix_clientes_id'), table_name='clientes')
    op.drop_index(op.f('ix_clientes_email'), table_name='clientes')
    op.drop_index(op.f('ix_agendamentos_id'), table_name='agendamentos')
    op.drop_index(op.f('ix_planilhas_mensais_mes'), table_name='planilhas_mensais')
    op.drop_index(op.f('ix_planilhas_mensais_id'), table_name='planilhas_mensais')
    op.drop_table('planilhas_mensais')
    # ### end Alembic commands ###
