from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Banco de Dados
    DATABASE_URL: str

    # Segurança JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Google OAuth 2.0
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/google/callback"

    # CORS — origens permitidas separadas por vírgula
    # Ex: "https://meu-app.vercel.app,https://outro-dominio.com"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    # Google Sheets — Service Account
    GOOGLE_SERVICE_ACCOUNT_FILE: str = "service_account.json"
    # ID da planilha mestre criada pelo usuário e compartilhada com a service account
    GOOGLE_SPREADSHEET_ID: str = ""


settings = Settings()
