from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.rotas_usuarios import router as usuarios_router
from api.rotas_clientes import router as clientes_router
from api.rotas_servicos import router as servicos_router
from api.rotas_profissionais import router as profissionais_router
from api.rotas_agendamentos import router as agendamentos_router
from api.rotas_relatorios import router as relatorios_router
from api.rotas_produtos import router as produtos_router
from api.rotas_tarefas import router as tarefas_router
from api.rotas_secoes import router as secoes_router
from api.rotas_dashboard import router as dashboard_router
from api.rotas_feriados import router as feriados_router
from api.rotas_preferencias import router as preferencias_router

from core.config import settings

app = FastAPI(
    title="SGK — Sistema de Gestão Kaneshiro",
    description="API para gestão de agendamentos, profissionais e caixa do salão.",
    version="0.1.0",
)

# --- CORS ---
# Em produção, defina ALLOWED_ORIGINS no painel da plataforma com a URL do frontend.
# Múltiplas origens separadas por vírgula: "https://a.vercel.app,https://b.com"
_origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
app.include_router(usuarios_router)
app.include_router(clientes_router)
app.include_router(servicos_router)
app.include_router(profissionais_router)
app.include_router(agendamentos_router)
app.include_router(relatorios_router)
app.include_router(produtos_router)
app.include_router(tarefas_router)
app.include_router(secoes_router)
app.include_router(dashboard_router)
app.include_router(feriados_router)
app.include_router(preferencias_router)


@app.get("/health", tags=["Status"])
def health_check():
    return {"status": "ok"}
