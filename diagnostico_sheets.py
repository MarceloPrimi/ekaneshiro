"""
Diagnóstico da service account — rode com:
  .\venv\Scripts\python diagnostico_sheets.py
"""
import json
import sys

# 1. Verifica se o arquivo existe e tem o formato correto
try:
    with open("service_account.json") as f:
        data = json.load(f)
    print("✅ service_account.json encontrado")
    print(f"   type: {data.get('type')}")
    print(f"   project_id: {data.get('project_id')}")
    print(f"   client_email: {data.get('client_email')}")
except FileNotFoundError:
    print("❌ service_account.json NÃO encontrado na raiz do projeto")
    sys.exit(1)
except json.JSONDecodeError as e:
    print(f"❌ JSON inválido: {e}")
    sys.exit(1)

if data.get("type") != "service_account":
    print(f"❌ Tipo errado: '{data.get('type')}' — deveria ser 'service_account'")
    sys.exit(1)

# 2. Testa autenticação
print("\n--- Testando autenticação ---")
try:
    from google.oauth2.service_account import Credentials
    creds = Credentials.from_service_account_file(
        "service_account.json",
        scopes=["https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"],
    )
    print("✅ Credenciais carregadas com sucesso")
except Exception as e:
    print(f"❌ Erro ao carregar credenciais: {e}")
    sys.exit(1)

# 3. Testa chamada real à API
print("\n--- Testando chamada à Sheets API ---")
try:
    from googleapiclient.discovery import build
    svc = build("sheets", "v4", credentials=creds)
    result = svc.spreadsheets().create(
        body={"properties": {"title": "SGK - Teste Diagnóstico"}},
        fields="spreadsheetId,spreadsheetUrl",
    ).execute()
    print(f"✅ Planilha criada com sucesso!")
    print(f"   ID: {result['spreadsheetId']}")
    print(f"   URL: {result['spreadsheetUrl']}")

    # Limpa o teste
    from googleapiclient.discovery import build as build2
    drive_svc = build2("drive", "v3", credentials=creds)
    drive_svc.files().delete(fileId=result["spreadsheetId"]).execute()
    print("   (planilha de teste removida)")
except Exception as e:
    print(f"❌ Erro na chamada à API: {e}")
    # Tenta extrair detalhes adicionais
    if hasattr(e, "error_details"):
        print(f"   Detalhes: {e.error_details}")
    if hasattr(e, "reason"):
        print(f"   Razão: {e.reason}")
    if hasattr(e, "status_code"):
        print(f"   Status: {e.status_code}")
    # Tenta criação via Drive API (workaround)
    print("\n--- Tentando criar via Drive API (alternativa) ---")
    try:
        from googleapiclient.discovery import build as build_drive
        drive_svc = build_drive("drive", "v3", credentials=creds)
        file_result = drive_svc.files().create(
            body={"name": "SGK - Teste Diagnóstico", "mimeType": "application/vnd.google-apps.spreadsheet"},
            fields="id,webViewLink",
        ).execute()
        print(f"✅ Planilha criada via Drive API!")
        print(f"   ID: {file_result['id']}")
        print(f"   URL: {file_result['webViewLink']}")
        # Remove o arquivo de teste
        drive_svc.files().delete(fileId=file_result["id"]).execute()
        print("   (planilha de teste removida)")
    except Exception as e4:
        print(f"❌ Criação via Drive também falhou: {e4}")
