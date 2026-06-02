import os, json

# Escreve service_account.json a partir da env var (precisa ser em runtime).
# É barato (apenas I/O de arquivo) e não impacta o cold start.
sa_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
if sa_json:
    with open("service_account.json", "w") as f:
        json.dump(json.loads(sa_json), f)

# Rodar as migrações no boot encarece o cold start (conexão + checagem no banco
# a cada vez que o serviço acorda no plano free). Por padrão mantemos o
# comportamento antigo para não quebrar nenhum deploy.
#
# Para acelerar o cold start em produção:
#   1) No Render, defina o "Pre-Deploy Command": python migrate.py
#   2) Defina a env var SKIP_MIGRATIONS_ON_BOOT=1
# Assim as migrações rodam uma vez por deploy, e não a cada cold start.
_skip = os.getenv("SKIP_MIGRATIONS_ON_BOOT", "").strip().lower() in ("1", "true", "yes")
if not _skip:
    from alembic.config import Config
    from alembic import command

    command.upgrade(Config("alembic.ini"), "head")