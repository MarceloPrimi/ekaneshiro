"""
Testes de feriados / recesso em lote.
"""
from db.models import Feriado


class TestFeriadoSimples:
    def test_cria_feriado(self, client, recep_h):
        resp = client.post(
            "/feriados/",
            json={"data": "2026-12-25", "nome": "Natal", "bloquear_agenda": True},
            headers=recep_h,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["data"] == "2026-12-25"
        assert data["bloquear_agenda"] is True

    def test_conflito_mesma_data(self, client, recep_h):
        client.post(
            "/feriados/",
            json={"data": "2026-12-25", "nome": "Natal", "bloquear_agenda": True},
            headers=recep_h,
        )
        resp = client.post(
            "/feriados/",
            json={"data": "2026-12-25", "nome": "Natal 2", "bloquear_agenda": True},
            headers=recep_h,
        )
        assert resp.status_code == 409


class TestFeriadoPeriodo:
    def test_cria_intervalo(self, client, db, recep_h):
        resp = client.post(
            "/feriados/periodo",
            json={
                "data_inicio": "2026-12-31",
                "data_fim": "2027-01-07",
                "nome": "Recesso Ano Novo",
                "bloquear_agenda": True,
            },
            headers=recep_h,
        )
        assert resp.status_code == 201, resp.text
        data = resp.json()
        assert data["total_dias"] == 8
        assert len(data["criados"]) == 8
        assert len(data["atualizados"]) == 0

        listados = client.get("/feriados/", headers=recep_h).json()
        datas = {f["data"] for f in listados}
        assert "2026-12-31" in datas
        assert "2027-01-07" in datas
        assert all(f["bloquear_agenda"] for f in listados if f["nome"] == "Recesso Ano Novo")

    def test_atualiza_dias_existentes(self, client, db, recep_h):
        db.add(Feriado(data="2027-01-01", nome="Antigo", bloquear_agenda=False))
        db.commit()

        resp = client.post(
            "/feriados/periodo",
            json={
                "data_inicio": "2027-01-01",
                "data_fim": "2027-01-02",
                "nome": "Recesso",
                "bloquear_agenda": True,
            },
            headers=recep_h,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["total_dias"] == 2
        assert len(data["atualizados"]) == 1
        assert len(data["criados"]) == 1
        assert data["atualizados"][0]["nome"] == "Recesso"
        assert data["atualizados"][0]["bloquear_agenda"] is True

    def test_fim_antes_inicio(self, client, recep_h):
        resp = client.post(
            "/feriados/periodo",
            json={
                "data_inicio": "2027-01-10",
                "data_fim": "2027-01-01",
                "nome": "Inválido",
                "bloquear_agenda": True,
            },
            headers=recep_h,
        )
        assert resp.status_code == 422

    def test_intervalo_muito_longo(self, client, recep_h):
        resp = client.post(
            "/feriados/periodo",
            json={
                "data_inicio": "2027-01-01",
                "data_fim": "2027-05-01",
                "nome": "Muito longo",
                "bloquear_agenda": True,
            },
            headers=recep_h,
        )
        assert resp.status_code == 422
