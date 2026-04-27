"""
Testes CRUD de clientes + validação de permissões.
"""
from tests.conftest import criar_cliente, criar_usuario, token_para
from db.models import RoleEnum


class TestCriarCliente:
    def test_recepcionista_pode_criar(self, client, recep_h):
        resp = client.post("/clientes/", json={"nome": "João"}, headers=recep_h)
        assert resp.status_code == 201
        assert resp.json()["nome"] == "João"

    def test_admin_pode_criar(self, client, admin_h):
        resp = client.post("/clientes/", json={"nome": "Maria"}, headers=admin_h)
        assert resp.status_code == 201

    def test_profissional_nao_pode_criar(self, client, db):
        prof_user = criar_usuario(db, email="p@sgk.com", role=RoleEnum.profissional)
        headers = token_para(prof_user)
        resp = client.post("/clientes/", json={"nome": "X"}, headers=headers)
        assert resp.status_code == 403

    def test_nao_autenticado_retorna_401(self, client):
        resp = client.post("/clientes/", json={"nome": "X"})
        assert resp.status_code == 401

    def test_cria_com_telefone_e_email(self, client, recep_h):
        payload = {"nome": "Ana", "telefone": "11999999999", "email": "ana@test.com"}
        resp = client.post("/clientes/", json=payload, headers=recep_h)
        assert resp.status_code == 201
        data = resp.json()
        assert data["telefone"] == "11999999999"
        assert data["email"] == "ana@test.com"

    def test_email_invalido_retorna_422(self, client, recep_h):
        resp = client.post(
            "/clientes/", json={"nome": "X", "email": "nao-e-email"}, headers=recep_h
        )
        assert resp.status_code == 422


class TestListarClientes:
    def test_qualquer_autenticado_pode_listar(self, client, db, recep_h):
        criar_cliente(db, "A")
        criar_cliente(db, "B")
        resp = client.get("/clientes/", headers=recep_h)
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_lista_vazia_sem_clientes(self, client, recep_h):
        resp = client.get("/clientes/", headers=recep_h)
        assert resp.json() == []


class TestBuscarCliente:
    def test_busca_por_id_existente(self, client, db, recep_h):
        c = criar_cliente(db, "Carlos")
        resp = client.get(f"/clientes/{c.id}", headers=recep_h)
        assert resp.status_code == 200
        assert resp.json()["nome"] == "Carlos"

    def test_id_inexistente_retorna_404(self, client, recep_h):
        resp = client.get("/clientes/9999", headers=recep_h)
        assert resp.status_code == 404


class TestAtualizarCliente:
    def test_atualiza_nome(self, client, db, recep_h):
        c = criar_cliente(db, "Antigo Nome")
        resp = client.patch(f"/clientes/{c.id}", json={"nome": "Novo Nome"}, headers=recep_h)
        assert resp.status_code == 200
        assert resp.json()["nome"] == "Novo Nome"

    def test_atualiza_apenas_campos_enviados(self, client, db, recep_h):
        c = criar_cliente(db, "Teste")
        client.patch(f"/clientes/{c.id}", json={"telefone": "11111"}, headers=recep_h)
        resp = client.get(f"/clientes/{c.id}", headers=recep_h)
        assert resp.json()["nome"] == "Teste"   # nome não mudou
        assert resp.json()["telefone"] == "11111"


class TestDeletarCliente:
    def test_recepcionista_pode_deletar(self, client, db, recep_h):
        c = criar_cliente(db, "Para Deletar")
        resp = client.delete(f"/clientes/{c.id}", headers=recep_h)
        assert resp.status_code == 204

    def test_deletar_inexistente_retorna_404(self, client, recep_h):
        resp = client.delete("/clientes/9999", headers=recep_h)
        assert resp.status_code == 404

    def test_apos_deletar_get_retorna_404(self, client, db, recep_h):
        c = criar_cliente(db)
        client.delete(f"/clientes/{c.id}", headers=recep_h)
        resp = client.get(f"/clientes/{c.id}", headers=recep_h)
        assert resp.status_code == 404
