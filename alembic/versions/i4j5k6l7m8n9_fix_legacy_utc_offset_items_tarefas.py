"""fix legacy utc offset on old schedule records

Revision ID: i4j5k6l7m8n9
Revises: h3i4j5k6l7m8
Create Date: 2026-05-27 00:00:00.000000
"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "i4j5k6l7m8n9"
down_revision = "h3i4j5k6l7m8"
branch_labels = None
depends_on = None


_CUTOFF = "2026-05-28 00:00:00"


def _apply_hour_shift(hours: int) -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == "mysql":
        if hours < 0:
            ia_expr_ini = f"DATE_SUB(ia.data_hora_inicio, INTERVAL {abs(hours)} HOUR)"
            ia_expr_fim = f"DATE_SUB(ia.data_hora_fim, INTERVAL {abs(hours)} HOUR)"
            t_expr_ini = f"DATE_SUB(data_hora_inicio, INTERVAL {abs(hours)} HOUR)"
            t_expr_fim = f"DATE_SUB(data_hora_fim, INTERVAL {abs(hours)} HOUR)"
        else:
            ia_expr_ini = f"DATE_ADD(ia.data_hora_inicio, INTERVAL {hours} HOUR)"
            ia_expr_fim = f"DATE_ADD(ia.data_hora_fim, INTERVAL {hours} HOUR)"
            t_expr_ini = f"DATE_ADD(data_hora_inicio, INTERVAL {hours} HOUR)"
            t_expr_fim = f"DATE_ADD(data_hora_fim, INTERVAL {hours} HOUR)"

        op.execute(
            f"""
            UPDATE itens_agendamento ia
            JOIN agendamentos a ON a.id = ia.agendamento_id
            SET
                ia.data_hora_inicio = {ia_expr_ini},
                ia.data_hora_fim = {ia_expr_fim}
            WHERE a.criado_em < '{_CUTOFF}'
            """
        )

        op.execute(
            f"""
            UPDATE tarefas_internas
            SET
                data_hora_inicio = {t_expr_ini},
                data_hora_fim = CASE
                    WHEN data_hora_fim IS NULL THEN NULL
                    ELSE {t_expr_fim}
                END
            WHERE criado_em < '{_CUTOFF}'
            """
        )
        return

    if dialect == "postgresql":
        sign = "+" if hours >= 0 else "-"
        abs_hours = abs(hours)

        op.execute(
            f"""
            UPDATE itens_agendamento ia
            SET
                data_hora_inicio = ia.data_hora_inicio {sign} INTERVAL '{abs_hours} hour',
                data_hora_fim = ia.data_hora_fim {sign} INTERVAL '{abs_hours} hour'
            FROM agendamentos a
            WHERE a.id = ia.agendamento_id
              AND a.criado_em < '{_CUTOFF}'
            """
        )

        op.execute(
            f"""
            UPDATE tarefas_internas
            SET
                data_hora_inicio = data_hora_inicio {sign} INTERVAL '{abs_hours} hour',
                data_hora_fim = CASE
                    WHEN data_hora_fim IS NULL THEN NULL
                    ELSE data_hora_fim {sign} INTERVAL '{abs_hours} hour'
                END
            WHERE criado_em < '{_CUTOFF}'
            """
        )
        return

    # Fallback para sqlite/outros dialetos
    if hours < 0:
        shift = f"-{abs(hours)} hours"
    else:
        shift = f"+{hours} hours"

    op.execute(
        f"""
        UPDATE itens_agendamento
        SET
            data_hora_inicio = datetime(data_hora_inicio, '{shift}'),
            data_hora_fim = datetime(data_hora_fim, '{shift}')
        WHERE EXISTS (
            SELECT 1
            FROM agendamentos a
            WHERE a.id = itens_agendamento.agendamento_id
              AND a.criado_em < '{_CUTOFF}'
        )
        """
    )

    op.execute(
        f"""
        UPDATE tarefas_internas
        SET
            data_hora_inicio = datetime(data_hora_inicio, '{shift}'),
            data_hora_fim = CASE
                WHEN data_hora_fim IS NULL THEN NULL
                ELSE datetime(data_hora_fim, '{shift}')
            END
        WHERE criado_em < '{_CUTOFF}'
        """
    )


def upgrade() -> None:
    # Corrige registros legados gravados com offset UTC (+3h no calendário).
    _apply_hour_shift(-3)


def downgrade() -> None:
    # Reverte o ajuste de horas aplicado no upgrade.
    _apply_hour_shift(3)
