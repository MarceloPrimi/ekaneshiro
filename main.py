from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.rotas_usuarios import router as usuarios_router
from api.rotas_clientes import router as clientes_router
from api.rotas_servicos import router as servicos_router
from api.rotas_profissionais import router as profissionais_router
from api.rotas_agendamentos import router as agendamentos_router
from api.rotas_relatorios import router as relatorios_router
from api.rotas_produtos import router as produtos_router

app = FastAPI(
    title="SGK — Sistema de Gestão Kaneshiro",
    description="API para gestão de agendamentos, profissionais e caixa do salão.",
    version="0.1.0",
)

# --- CORS (ajuste origins em produção) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
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


@app.get("/health", tags=["Status"])
def health_check():
    return {"status": "ok"}
