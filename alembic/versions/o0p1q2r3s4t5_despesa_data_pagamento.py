"""rename despesas.data -> data_pagamento (nullable when pendente)

Revision ID: o0p1q2r3s4t5
Revises: n9o0p1q2r3s4
Create Date: 2026-10-04
"""

from alembic import op


revision = "o0p1q2r3s4t5"
down_revision = "n9o0p1q2r3s4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # MySQL/TiDB: CHANGE permite renomear + tornar nullable em um passo
    op.execute(
        "ALTER TABLE despesas CHANGE COLUMN `data` `data_pagamento` DATE NULL"
    )
    op.execute("UPDATE despesas SET data_pagamento = NULL WHERE status = 'pendente'")


def downgrade() -> None:
    op.execute(
        "UPDATE despesas SET data_pagamento = CURRENT_DATE "
        "WHERE data_pagamento IS NULL"
    )
    op.execute(
        "ALTER TABLE despesas CHANGE COLUMN `data_pagamento` `data` DATE NOT NULL"
    )
