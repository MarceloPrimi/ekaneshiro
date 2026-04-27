import os, json

sa_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
if sa_json:
    with open("service_account.json", "w") as f:
        json.dump(json.loads(sa_json), f)