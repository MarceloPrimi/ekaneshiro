"""
Fixtures compartilhadas entre todos os testes.

Banco: SQLite in-memory (sem MySQL necessário).
Isolamento: tabelas criadas/dropadas a cada função de teste.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from core.security import create_access_token, hash_password
from db.database import Base, get_db
from db.models import (
    Cliente,
    Profissional,
    ProfissionalServico,
    RoleEnum,
    Servico,
    Usuario,
)
from main import app

# ---------------------------------------------------------------------------
# Engine SQLite in-memory (StaticPool = mesma conexão em toda a sessão)
# ---------------------------------------------------------------------------
_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_Session = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


# ---------------------------------------------------------------------------
# Fixtures de banco e cliente HTTP
# ---------------------------------------------------------------------------

@pytest.fixture()
def db():
    """Sessão de banco limpa por teste (cria e dropa todas as tabelas)."""
    Base.metadata.create_all(bind=_engine)
    session = _Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=_engine)


@pytest.fixture()
def client(db):
    """TestClient com injeção de dependência do banco de teste."""
    def _override():
        yield db

    app.dependency_overrides[get_db] = _override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Helpers reutilizáveis
# ---------------------------------------------------------------------------

def criar_usuario(
    db,
    nome: str = "Usuário",
    email: str = "user@sgk.com",
    password: str = "Senha@123",
    role: RoleEnum = RoleEnum.admin,
    ativo: bool = True,
) -> Usuario:
    u = Usuario(
        nome=nome,
        email=email,
        hashed_password=hash_password(password),
        role=role,
        ativo=ativo,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def token_para(user: Usuario) -> dict:
    token = create_access_token({"sub": user.email, "role": user.role.value})
    return {"Authorization": f"Bearer {token}"}


def criar_servico(db, nome="Corte", duracao=60, preco="50.00") -> Servico:
    s = Servico(nome=nome, duracao_minutos=duracao, preco=preco)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def criar_profissional(db, nome="Cabeleireiro", usuario_id=None) -> Profissional:
    p = Profissional(nome=nome, usuario_id=usuario_id)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def criar_cliente(db, nome="Cliente Teste") -> Cliente:
    c = Cliente(nome=nome)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def habilitar_servico(db, profissional_id: int, servico_id: int) -> None:
    db.add(ProfissionalServico(profissional_id=profissional_id, servico_id=servico_id))
    db.commit()


# ---------------------------------------------------------------------------
# Fixtures de usuários e headers
# ---------------------------------------------------------------------------

@pytest.fixture()
def admin(db):
    return criar_usuario(db, nome="Admin", email="admin@sgk.com", role=RoleEnum.admin)


@pytest.fixture()
def recepcionista(db):
    return criar_usuario(db, nome="Recep", email="recep@sgk.com", role=RoleEnum.recepcionista)


@pytest.fixture()
def admin_h(admin):
    return token_para(admin)


@pytest.fixture()
def recep_h(recepcionista):
    return token_para(recepcionista)
