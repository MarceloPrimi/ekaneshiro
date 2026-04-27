"""
Testes dos endpoints de usuários e autenticação.
"""
from tests.conftest import criar_usuario, token_para
from db.models import RoleEnum


class TestLogin:
    def test_login_sucesso_retorna_token(self, client, db):
        criar_usuario(db, email="u@sgk.com", password="Senha@123")
        resp = client.post(
            "/usuarios/login",
            data={"username": "u@sgk.com", "password": "Senha@123"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_senha_errada_retorna_401(self, client, db):
        criar_usuario(db, email="u@sgk.com", password="Senha@123")
        resp = client.post(
            "/usuarios/login",
            data={"username": "u@sgk.com", "password": "senhaErrada"},
        )
        assert resp.status_code == 401

    def test_login_email_inexistente_retorna_401(self, client):
        resp = client.post(
            "/usuarios/login",
            data={"username": "naoexiste@sgk.com", "password": "qualquer"},
        )
        assert resp.status_code == 401

    def test_login_usuario_inativo_retorna_401(self, client, db):
        criar_usuario(db, email="inativo@sgk.com", password="Senha@123", ativo=False)
        resp = client.post(
            "/usuarios/login",
            data={"username": "inativo@sgk.com", "password": "Senha@123"},
        )
        assert resp.status_code == 401

    def test_login_nao_expoe_hashed_password(self, client, db):
        criar_usuario(db, email="u@sgk.com", password="Senha@123")
        resp = client.post(
            "/usuarios/login",
            data={"username": "u@sgk.com", "password": "Senha@123"},
        )
        assert "hashed_password" not in resp.text
        assert "password" not in resp.json()


class TestCriarUsuario:
    def test_admin_pode_criar_usuario(self, client, admin_h):
        resp = client.post(
            "/usuarios/",
            json={"nome": "Novo", "email": "novo@sgk.com", "password": "Senha@123"},
            headers=admin_h,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "novo@sgk.com"
        assert "hashed_password" not in data
        assert "password" not in data

    def test_recepcionista_nao_pode_criar_usuario(self, client, recep_h):
        resp = client.post(
            "/usuarios/",
            json={"nome": "X", "email": "x@sgk.com", "password": "Senha@123"},
            headers=recep_h,
        )
        assert resp.status_code == 403

    def test_email_duplicado_retorna_409(self, client, admin_h, admin):
        resp = client.post(
            "/usuarios/",
            json={"nome": "Copia", "email": admin.email, "password": "Senha@123"},
            headers=admin_h,
        )
        assert resp.status_code == 409

    def test_email_invalido_retorna_422(self, client, admin_h):
        resp = client.post(
            "/usuarios/",
            json={"nome": "X", "email": "nao-e-email", "password": "Senha@123"},
            headers=admin_h,
        )
        assert resp.status_code == 422

    def test_role_padrao_e_recepcionista(self, client, admin_h):
        resp = client.post(
            "/usuarios/",
            json={"nome": "Sem Role", "email": "semrole@sgk.com", "password": "Senha@123"},
            headers=admin_h,
        )
        assert resp.json()["role"] == "recepcionista"


class TestMe:
    def test_me_retorna_usuario_autenticado(self, client, admin, admin_h):
        resp = client.get("/usuarios/me", headers=admin_h)
        assert resp.status_code == 200
        assert resp.json()["email"] == admin.email

    def test_me_sem_autenticacao_retorna_401(self, client):
        resp = client.get("/usuarios/me")
        assert resp.status_code == 401

    def test_me_nao_expoe_hashed_password(self, client, admin_h):
        resp = client.get("/usuarios/me", headers=admin_h)
        assert "hashed_password" not in resp.json()


class TestListarUsuarios:
    def test_admin_pode_listar(self, client, admin_h):
        resp = client.get("/usuarios/", headers=admin_h)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_recepcionista_nao_pode_listar(self, client, recep_h):
        resp = client.get("/usuarios/", headers=recep_h)
        assert resp.status_code == 403


class TestAtualizarUsuario:
    def test_admin_pode_desativar_usuario(self, client, db, admin_h):
        outro = criar_usuario(db, email="outro@sgk.com", role=RoleEnum.recepcionista)
        resp = client.patch(f"/usuarios/{outro.id}", json={"ativo": False}, headers=admin_h)
        assert resp.status_code == 200
        assert resp.json()["ativo"] is False

    def test_usuario_desativado_nao_consegue_logar(self, client, db, admin_h):
        outro = criar_usuario(db, email="outro@sgk.com", password="Senha@123", role=RoleEnum.recepcionista)
        client.patch(f"/usuarios/{outro.id}", json={"ativo": False}, headers=admin_h)
        resp = client.post(
            "/usuarios/login",
            data={"username": "outro@sgk.com", "password": "Senha@123"},
        )
        assert resp.status_code == 401

    def test_usuario_inexistente_retorna_404(self, client, admin_h):
        resp = client.patch("/usuarios/999", json={"ativo": False}, headers=admin_h)
        assert resp.status_code == 404
