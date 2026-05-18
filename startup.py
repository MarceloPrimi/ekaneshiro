import os, json
from alembic.config import Config
from alembic import command

sa_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
if sa_json:
    with open("service_account.json", "w") as f:
        json.dump(json.loads(sa_json), f)

alembic_cfg = Config("alembic.ini")
command.upgrade(alembic_cfg, "head")