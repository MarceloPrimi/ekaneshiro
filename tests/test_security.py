"""
Testes de segurança: bcrypt, JWT e proteção de endpoints.

Categorias:
  - Hashing de senhas (propriedades do bcrypt)
  - JWT (criação, decodificação, expiração, adulteração)
  - Endpoints protegidos (sem token → 401)
  - RBAC (role errado → 403)
  - SQL Injection (deve retornar 401, nunca 500 ou dados)
  - XSS (payload armazenado como texto puro, não executado)
"""
from datetime import timedelta

import pytest

from core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from tests.conftest import criar_usuario, token_para
from db.models import RoleEnum


# ── bcrypt ──────────────────────────────────────────────────────────────────

class TestHashPassword:
    def test_hash_nao_igual_ao_texto_puro(self):
        assert hash_password("senha123") != "senha123"

    def test_hashes_diferentes_para_mesma_senha(self):
        """bcrypt usa salt aleatório — dois hashes da mesma senha devem diferir."""
        h1 = hash_password("senha123")
        h2 = hash_password("senha123")
        assert h1 != h2

    def test_verify_senha_correta(self):
        h = hash_password("Senha@123")
        assert verify_password("Senha@123", h) is True

    def test_verify_senha_errada(self):
        h = hash_password("Senha@123")
        assert verify_password("outra_senha", h) is False

    def test_hash_comeca_com_bcrypt(self):
        """Hash deve ser bcrypt ($2b$)."""
        h = hash_password("qualquer")
        assert h.startswith("$2b$")


# ── JWT ─────────────────────────────────────────────────────────────────────

class TestJWT:
    def test_criar_e_decodificar_token(self):
        payload = {"sub": "user@test.com", "role": "admin"}
        token = create_access_token(payload)
        decoded = decode_access_token(token)
        assert decoded is not None
        assert decoded["sub"] == "user@test.com"
        assert decoded["role"] == "admin"

    def test_token_expirado_retorna_none(self):
        token = create_access_token({"sub": "x@x.com"}, expires_delta=timedelta(seconds=-1))
        assert decode_access_token(token) is None

    def test_token_invalido_retorna_none(self):
        assert decode_access_token("token.invalido.qualquer") is None

    def test_token_adulterado_retorna_none(self):
        token = create_access_token({"sub": "user@test.com"})
        partes = token.split(".")
        # Adultera o payload (parte do meio)
        partes[1] = partes[1][:-3] + "xxx"
        adulterado = ".".join(partes)
        assert decode_access_token(adulterado) is None

    def test_token_vazio_retorna_none(self):
        assert decode_access_token("") is None


# ── Endpoints protegidos (sem autenticação → 401) ───────────────────────────

class TestEndpointsProtegidos:
    ENDPOINTS_PROTEGIDOS = [
        ("GET",    "/usuarios/me"),
        ("GET",    "/usuarios/"),
        ("GET",    "/clientes/"),
        ("POST",   "/clientes/"),
        ("GET",    "/servicos/"),
        ("POST",   "/servicos/"),
        ("GET",    "/profissionais/"),
        ("POST",   "/profissionais/"),
        ("GET",    "/agendamentos/"),
        ("POST",   "/agendamentos/"),
    ]

    @pytest.mark.parametrize("method,url", ENDPOINTS_PROTEGIDOS)
    def test_sem_token_retorna_401(self, client, method, url):
        kwargs = {} if method.upper() == "GET" else {"json": {}}
        resp = getattr(client, method.lower())(url, **kwargs)
        assert resp.status_code == 401, (
            f"{method} {url} deveria retornar 401 sem autenticação, "
            f"mas retornou {resp.status_code}"
        )

    def test_token_invalido_retorna_401(self, client):
        headers = {"Authorization": "Bearer token_completamente_invalido"}
        resp = client.get("/usuarios/me", headers=headers)
        assert resp.status_code == 401

    def test_token_sem_prefixo_bearer_retorna_401(self, client):
        from core.security import create_access_token
        token = create_access_token({"sub": "a@a.com", "role": "admin"})
        headers = {"Authorization": token}  # sem "Bearer "
        resp = client.get("/usuarios/me", headers=headers)
        assert resp.status_code == 401


# ── RBAC (role errado → 403) ─────────────────────────────────────────────────

class TestRBAC:
    def test_recepcionista_nao_pode_criar_usuario(self, client, recep_h):
        resp = client.post(
            "/usuarios/",
            json={"nome": "X", "email": "x@x.com", "password": "Senha@123"},
            headers=recep_h,
        )
        assert resp.status_code == 403

    def test_recepcionista_nao_pode_listar_usuarios(self, client, recep_h):
        resp = client.get("/usuarios/", headers=recep_h)
        assert resp.status_code == 403

    def test_recepcionista_nao_pode_criar_servico(self, client, recep_h):
        resp = client.post(
            "/servicos/",
            json={"nome": "Corte", "duracao_minutos": 60, "preco": "50.00"},
            headers=recep_h,
        )
        assert resp.status_code == 403

    def test_recepcionista_nao_pode_criar_profissional(self, client, recep_h):
        resp = client.post("/profissionais/", json={"nome": "X"}, headers=recep_h)
        assert resp.status_code == 403


# ── SQL Injection ────────────────────────────────────────────────────────────

class TestSQLInjection:
    PAYLOADS = [
        "' OR '1'='1",
        "'; DROP TABLE usuarios; --",
        "' UNION SELECT * FROM usuarios --",
        "admin'--",
    ]

    @pytest.mark.parametrize("payload", PAYLOADS)
    def test_sql_injection_no_login_retorna_401_nao_500(self, client, payload):
        """SQL injection deve ser ignorado pelo ORM parameterizado — nunca 500."""
        resp = client.post(
            "/usuarios/login",
            data={"username": payload, "password": payload},
        )
        assert resp.status_code == 401
        # Garante que nenhum dado sensível vazou
        body = resp.text
        assert "hashed_password" not in body
        assert "SELECT" not in body.upper()

    def test_sql_injection_em_nome_de_cliente_tratado_como_texto(self, client, recep_h):
        """Payload SQL em campos string deve ser armazenado literalmente."""
        payload = "'; DROP TABLE clientes; --"
        resp = client.post("/clientes/", json={"nome": payload}, headers=recep_h)
        assert resp.status_code == 201
        assert resp.json()["nome"] == payload


# ── XSS ─────────────────────────────────────────────────────────────────────

class TestXSS:
    def test_xss_em_nome_armazenado_como_texto_puro(self, client, recep_h):
        """
        O backend não executa nem escapa HTML — armazena como texto puro.
        A proteção contra XSS é responsabilidade do frontend (encoding na renderização).
        """
        xss = "<script>alert('xss')</script>"
        resp = client.post("/clientes/", json={"nome": xss}, headers=recep_h)
        assert resp.status_code == 201
        assert resp.json()["nome"] == xss

    def test_xss_em_observacoes_agendamento(self, client, db, recep_h):
        """Observações com XSS também são armazenadas como texto puro."""
        from tests.conftest import (
            criar_cliente, criar_profissional, criar_servico, habilitar_servico
        )
        cliente = criar_cliente(db)
        servico = criar_servico(db)
        prof = criar_profissional(db)
        habilitar_servico(db, prof.id, servico.id)

        xss = "<img src=x onerror=alert(1)>"
        resp = client.post(
            "/agendamentos/",
            json={
                "cliente_id": cliente.id,
                "observacoes": xss,
                "itens": [{
                    "servico_id": servico.id,
                    "profissional_id": prof.id,
                    "data_hora_inicio": "2027-06-01T10:00:00",
                }],
            },
            headers=recep_h,
        )
        assert resp.status_code == 201
        assert resp.json()["observacoes"] == xss
