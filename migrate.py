"""Aplica as migrações do Alembic até a última versão.

Use como Pre-Deploy Command no Render (ou em qualquer pipeline de deploy):

    python migrate.py

Rodar aqui (e não no boot do serviço) evita pagar o custo de migração a cada
cold start do plano free. Combine com a env var SKIP_MIGRATIONS_ON_BOOT=1.
"""
from alembic.config import Config
from alembic import command


def run() -> None:
    command.upgrade(Config("alembic.ini"), "head")


if __name__ == "__main__":
    run()
