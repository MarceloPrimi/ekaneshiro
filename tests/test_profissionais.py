"""
Testes CRUD de profissionais + vínculo profissional↔serviço.
"""
from tests.conftest import criar_profissional, criar_servico, habilitar_servico


class TestCriarProfissional:
    def test_admin_pode_criar(self, client, admin_h):
        resp = client.post("/profissionais/", json={"nome": "Ana"}, headers=admin_h)
        assert resp.status_code == 201
        data = resp.json()
        assert data["nome"] == "Ana"
        assert data["ativo"] is True

    def test_recepcionista_nao_pode_criar(self, client, recep_h):
        resp = client.post("/profissionais/", json={"nome": "X"}, headers=recep_h)
        assert resp.status_code == 403

    def test_nao_autenticado_retorna_401(self, client):
        resp = client.post("/profissionais/", json={"nome": "X"})
        assert resp.status_code == 401


class TestListarProfissionais:
    def test_lista_apenas_ativos_por_padrao(self, client, db, recep_h, admin_h):
        criar_profissional(db, nome="Ativo")
        p2 = criar_profissional(db, nome="Inativo")
        client.patch(f"/profissionais/{p2.id}", json={"ativo": False}, headers=admin_h)

        resp = client.get("/profissionais/", headers=recep_h)
        assert resp.status_code == 200
        nomes = [p["nome"] for p in resp.json()]
        assert "Ativo" in nomes
        assert "Inativo" not in nomes

    def test_lista_todos_com_flag_false(self, client, db, recep_h, admin_h):
        criar_profissional(db, nome="P1")
        p2 = criar_profissional(db, nome="P2")
        client.patch(f"/profissionais/{p2.id}", json={"ativo": False}, headers=admin_h)

        resp = client.get("/profissionais/?apenas_ativos=false", headers=recep_h)
        nomes = [p["nome"] for p in resp.json()]
        assert "P1" in nomes
        assert "P2" in nomes


class TestBuscarProfissional:
    def test_retorna_profissional_com_servicos(self, client, db, recep_h):
        p = criar_profissional(db, nome="Estilista")
        s = criar_servico(db, nome="Escova")
        habilitar_servico(db, p.id, s.id)

        resp = client.get(f"/profissionais/{p.id}", headers=recep_h)
        assert resp.status_code == 200
        data = resp.json()
        assert data["nome"] == "Estilista"
        assert len(data["servicos"]) == 1
        assert data["servicos"][0]["nome"] == "Escova"

    def test_profissional_sem_servicos_retorna_lista_vazia(self, client, db, recep_h):
        p = criar_profissional(db)
        resp = client.get(f"/profissionais/{p.id}", headers=recep_h)
        assert resp.json()["servicos"] == []

    def test_inexistente_retorna_404(self, client, recep_h):
        resp = client.get("/profissionais/9999", headers=recep_h)
        assert resp.status_code == 404


class TestAtualizarProfissional:
    def test_admin_pode_atualizar_nome(self, client, db, admin_h):
        p = criar_profissional(db, nome="Antigo")
        resp = client.patch(f"/profissionais/{p.id}", json={"nome": "Novo"}, headers=admin_h)
        assert resp.status_code == 200
        assert resp.json()["nome"] == "Novo"

    def test_admin_pode_desativar(self, client, db, admin_h):
        p = criar_profissional(db)
        resp = client.patch(f"/profissionais/{p.id}", json={"ativo": False}, headers=admin_h)
        assert resp.json()["ativo"] is False

    def test_recepcionista_nao_pode_atualizar(self, client, db, recep_h):
        p = criar_profissional(db)
        resp = client.patch(f"/profissionais/{p.id}", json={"nome": "X"}, headers=recep_h)
        assert resp.status_code == 403


class TestVinculoServico:
    def test_admin_habilita_servico(self, client, db, admin_h, recep_h):
        p = criar_profissional(db)
        s = criar_servico(db)
        resp = client.post(
            f"/profissionais/{p.id}/servicos/{s.id}", headers=admin_h
        )
        assert resp.status_code == 204

        # Confirma via GET
        get = client.get(f"/profissionais/{p.id}", headers=recep_h)
        assert len(get.json()["servicos"]) == 1

    def test_vincular_duplicado_retorna_409(self, client, db, admin_h):
        p = criar_profissional(db)
        s = criar_servico(db)
        habilitar_servico(db, p.id, s.id)
        resp = client.post(f"/profissionais/{p.id}/servicos/{s.id}", headers=admin_h)
        assert resp.status_code == 409

    def test_vincular_servico_inexistente_retorna_404(self, client, db, admin_h):
        p = criar_profissional(db)
        resp = client.post(f"/profissionais/{p.id}/servicos/9999", headers=admin_h)
        assert resp.status_code == 404

    def test_vincular_profissional_inexistente_retorna_404(self, client, db, admin_h):
        s = criar_servico(db)
        resp = client.post(f"/profissionais/9999/servicos/{s.id}", headers=admin_h)
        assert resp.status_code == 404

    def test_admin_remove_servico(self, client, db, admin_h, recep_h):
        p = criar_profissional(db)
        s = criar_servico(db)
        habilitar_servico(db, p.id, s.id)

        resp = client.delete(f"/profissionais/{p.id}/servicos/{s.id}", headers=admin_h)
        assert resp.status_code == 204

        get = client.get(f"/profissionais/{p.id}", headers=recep_h)
        assert get.json()["servicos"] == []

    def test_remover_vinculo_inexistente_retorna_404(self, client, db, admin_h):
        p = criar_profissional(db)
        s = criar_servico(db)
        resp = client.delete(f"/profissionais/{p.id}/servicos/{s.id}", headers=admin_h)
        assert resp.status_code == 404

    def test_recepcionista_nao_pode_habilitar_servico(self, client, db, recep_h):
        p = criar_profissional(db)
        s = criar_servico(db)
        resp = client.post(f"/profissionais/{p.id}/servicos/{s.id}", headers=recep_h)
        assert resp.status_code == 403
