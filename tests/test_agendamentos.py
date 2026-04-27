"""
Testes do Motor de Agendamento:
  - Criação com múltiplos serviços (transação ACID)
  - Detecção de conflito de horário (boundary conditions)
  - Validação de vínculo profissional↔serviço
  - Transições de status com RBAC
  - Registro de pagamento
"""
import pytest

from db.models import Profissional, RoleEnum
from tests.conftest import (
    criar_cliente,
    criar_profissional,
    criar_servico,
    criar_usuario,
    habilitar_servico,
    token_para,
)


# ---------------------------------------------------------------------------
# Fixture: setup completo para testes de agendamento
# ---------------------------------------------------------------------------

@pytest.fixture()
def setup(db, recepcionista):
    """Retorna cliente, profissional, servico já vinculados."""
    cliente = criar_cliente(db, "Cliente Teste")
    servico = criar_servico(db, nome="Corte", duracao=60, preco="50.00")
    prof = criar_profissional(db, nome="Cabeleireiro")
    habilitar_servico(db, prof.id, servico.id)
    return {"cliente": cliente, "servico": servico, "profissional": prof}


def _payload_agendamento(setup, inicio="2027-06-01T10:00:00", obs=None):
    return {
        "cliente_id": setup["cliente"].id,
        "observacoes": obs,
        "itens": [{
            "servico_id": setup["servico"].id,
            "profissional_id": setup["profissional"].id,
            "data_hora_inicio": inicio,
        }],
    }


# ---------------------------------------------------------------------------
# Criação
# ---------------------------------------------------------------------------

class TestCriarAgendamento:
    def test_cria_com_sucesso(self, client, setup, recep_h):
        resp = client.post("/agendamentos/", json=_payload_agendamento(setup), headers=recep_h)
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "pendente"
        assert len(data["itens"]) == 1
        item = data["itens"][0]
        assert item["data_hora_inicio"] == "2027-06-01T10:00:00"
        assert item["data_hora_fim"] == "2027-06-01T11:00:00"  # +60 min

    def test_cria_multiplos_itens_em_uma_transacao(self, client, db, recep_h):
        """Dois serviços com profissionais diferentes — uma única requisição."""
        cliente = criar_cliente(db)
        s1 = criar_servico(db, nome="Corte", duracao=60)
        s2 = criar_servico(db, nome="Escova", duracao=30)
        p1 = criar_profissional(db, nome="P1")
        p2 = criar_profissional(db, nome="P2")
        habilitar_servico(db, p1.id, s1.id)
        habilitar_servico(db, p2.id, s2.id)

        payload = {
            "cliente_id": cliente.id,
            "itens": [
                {"servico_id": s1.id, "profissional_id": p1.id, "data_hora_inicio": "2027-06-01T10:00:00"},
                {"servico_id": s2.id, "profissional_id": p2.id, "data_hora_inicio": "2027-06-01T10:00:00"},
            ],
        }
        resp = client.post("/agendamentos/", json=payload, headers=recep_h)
        assert resp.status_code == 201
        assert len(resp.json()["itens"]) == 2

    def test_itens_vazios_retorna_422(self, client, db, recep_h):
        cliente = criar_cliente(db)
        resp = client.post(
            "/agendamentos/",
            json={"cliente_id": cliente.id, "itens": []},
            headers=recep_h,
        )
        assert resp.status_code == 422

    def test_servico_nao_habilitado_para_profissional_retorna_422(self, client, db, recep_h):
        cliente = criar_cliente(db)
        servico = criar_servico(db)
        prof = criar_profissional(db)
        # Não chama habilitar_servico

        resp = client.post(
            "/agendamentos/",
            json={
                "cliente_id": cliente.id,
                "itens": [{
                    "servico_id": servico.id,
                    "profissional_id": prof.id,
                    "data_hora_inicio": "2027-06-01T10:00:00",
                }],
            },
            headers=recep_h,
        )
        assert resp.status_code == 422

    def test_profissional_inativo_retorna_404(self, client, db, recep_h, admin_h):
        cliente = criar_cliente(db)
        servico = criar_servico(db)
        prof = criar_profissional(db)
        habilitar_servico(db, prof.id, servico.id)
        client.patch(f"/profissionais/{prof.id}", json={"ativo": False}, headers=admin_h)

        resp = client.post(
            "/agendamentos/",
            json={
                "cliente_id": cliente.id,
                "itens": [{
                    "servico_id": servico.id,
                    "profissional_id": prof.id,
                    "data_hora_inicio": "2027-06-01T10:00:00",
                }],
            },
            headers=recep_h,
        )
        assert resp.status_code == 404

    def test_nao_autenticado_retorna_401(self, client, setup):
        resp = client.post("/agendamentos/", json=_payload_agendamento(setup))
        assert resp.status_code == 401

    def test_data_hora_fim_calculada_pela_duracao(self, client, db, recep_h):
        """Serviço de 90 min: fim deve ser inicio + 90 min."""
        cliente = criar_cliente(db)
        servico = criar_servico(db, duracao=90)
        prof = criar_profissional(db)
        habilitar_servico(db, prof.id, servico.id)

        resp = client.post(
            "/agendamentos/",
            json={
                "cliente_id": cliente.id,
                "itens": [{
                    "servico_id": servico.id,
                    "profissional_id": prof.id,
                    "data_hora_inicio": "2027-06-01T09:00:00",
                }],
            },
            headers=recep_h,
        )
        assert resp.status_code == 201
        assert resp.json()["itens"][0]["data_hora_fim"] == "2027-06-01T10:30:00"


# ---------------------------------------------------------------------------
# Detecção de Conflito (regra de negócio mais crítica)
# ---------------------------------------------------------------------------

class TestConflito:
    def test_conflito_total_retorna_409(self, client, setup, recep_h):
        """Mesmo horário exato → conflito."""
        client.post("/agendamentos/", json=_payload_agendamento(setup, "2027-06-01T10:00:00"), headers=recep_h)
        resp = client.post("/agendamentos/", json=_payload_agendamento(setup, "2027-06-01T10:00:00"), headers=recep_h)
        assert resp.status_code == 409

    def test_conflito_sobreposicao_parcial(self, client, setup, recep_h):
        """Segundo começa no meio do primeiro (10:30 dentro de 10:00–11:00)."""
        client.post("/agendamentos/", json=_payload_agendamento(setup, "2027-06-01T10:00:00"), headers=recep_h)
        resp = client.post("/agendamentos/", json=_payload_agendamento(setup, "2027-06-01T10:30:00"), headers=recep_h)
        assert resp.status_code == 409

    def test_sem_conflito_logo_apos_termino(self, client, setup, recep_h):
        """Segundo começa exatamente quando o primeiro termina (11:00) → sem conflito."""
        client.post("/agendamentos/", json=_payload_agendamento(setup, "2027-06-01T10:00:00"), headers=recep_h)
        resp = client.post("/agendamentos/", json=_payload_agendamento(setup, "2027-06-01T11:00:00"), headers=recep_h)
        assert resp.status_code == 201

    def test_sem_conflito_antes_do_inicio(self, client, setup, recep_h):
        """Segundo termina antes do primeiro começar → sem conflito."""
        client.post("/agendamentos/", json=_payload_agendamento(setup, "2027-06-01T12:00:00"), headers=recep_h)
        # Serviço 60min → 09:00-10:00, termina antes das 12:00
        resp = client.post("/agendamentos/", json=_payload_agendamento(setup, "2027-06-01T09:00:00"), headers=recep_h)
        assert resp.status_code == 201

    def test_profissionais_diferentes_nao_conflitam(self, client, db, recep_h):
        """Mesmo horário, profissionais diferentes → sem conflito."""
        cliente = criar_cliente(db)
        servico = criar_servico(db, duracao=60)
        p1 = criar_profissional(db, nome="P1")
        p2 = criar_profissional(db, nome="P2")
        habilitar_servico(db, p1.id, servico.id)
        habilitar_servico(db, p2.id, servico.id)

        for prof_id in [p1.id, p2.id]:
            resp = client.post(
                "/agendamentos/",
                json={
                    "cliente_id": cliente.id,
                    "itens": [{
                        "servico_id": servico.id,
                        "profissional_id": prof_id,
                        "data_hora_inicio": "2027-06-01T10:00:00",
                    }],
                },
                headers=recep_h,
            )
            assert resp.status_code == 201

    def test_cancelado_nao_bloqueia_horario(self, client, setup, recep_h):
        """Agendamento cancelado não deve travar o horário para novos agendamentos."""
        resp1 = client.post("/agendamentos/", json=_payload_agendamento(setup, "2027-06-01T10:00:00"), headers=recep_h)
        ag_id = resp1.json()["id"]
        client.patch(f"/agendamentos/{ag_id}/status", json={"status": "cancelado"}, headers=recep_h)

        resp2 = client.post("/agendamentos/", json=_payload_agendamento(setup, "2027-06-01T10:00:00"), headers=recep_h)
        assert resp2.status_code == 201


# ---------------------------------------------------------------------------
# Atualização de Status + RBAC
# ---------------------------------------------------------------------------

class TestStatusAgendamento:
    def test_recepcionista_pode_confirmar(self, client, setup, recep_h):
        ag = client.post("/agendamentos/", json=_payload_agendamento(setup), headers=recep_h).json()
        resp = client.patch(f"/agendamentos/{ag['id']}/status", json={"status": "confirmado"}, headers=recep_h)
        assert resp.status_code == 200
        assert resp.json()["status"] == "confirmado"

    def test_recepcionista_pode_cancelar(self, client, setup, recep_h):
        ag = client.post("/agendamentos/", json=_payload_agendamento(setup), headers=recep_h).json()
        resp = client.patch(f"/agendamentos/{ag['id']}/status", json={"status": "cancelado"}, headers=recep_h)
        assert resp.status_code == 200
        assert resp.json()["status"] == "cancelado"

    def test_profissional_vinculado_pode_marcar_concluido(self, client, db, recep_h):
        """Profissional que está no item do agendamento pode marcá-lo como concluído."""
        prof_usuario = criar_usuario(db, email="pf@sgk.com", role=RoleEnum.profissional)
        prof = criar_profissional(db, usuario_id=prof_usuario.id)
        servico = criar_servico(db)
        habilitar_servico(db, prof.id, servico.id)
        cliente = criar_cliente(db)

        ag = client.post(
            "/agendamentos/",
            json={
                "cliente_id": cliente.id,
                "itens": [{
                    "servico_id": servico.id,
                    "profissional_id": prof.id,
                    "data_hora_inicio": "2027-06-01T10:00:00",
                }],
            },
            headers=recep_h,
        ).json()

        prof_h = token_para(prof_usuario)
        resp = client.patch(
            f"/agendamentos/{ag['id']}/status",
            json={"status": "concluido"},
            headers=prof_h,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "concluido"

    def test_profissional_nao_pode_confirmar_apenas_concluir(self, client, db, setup, recep_h):
        """Profissional só pode usar status 'concluido'."""
        prof_usuario = criar_usuario(db, email="pf2@sgk.com", role=RoleEnum.profissional)
        # Cria profissional diferente do que está no agendamento
        criar_profissional(db, usuario_id=prof_usuario.id)

        ag = client.post("/agendamentos/", json=_payload_agendamento(setup), headers=recep_h).json()
        prof_h = token_para(prof_usuario)

        resp = client.patch(
            f"/agendamentos/{ag['id']}/status",
            json={"status": "confirmado"},
            headers=prof_h,
        )
        assert resp.status_code == 403

    def test_agendamento_inexistente_retorna_404(self, client, recep_h):
        resp = client.patch("/agendamentos/9999/status", json={"status": "confirmado"}, headers=recep_h)
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Pagamento
# ---------------------------------------------------------------------------

class TestPagamento:
    def test_registrar_pagamento_confirma_agendamento(self, client, setup, recep_h):
        ag = client.post("/agendamentos/", json=_payload_agendamento(setup), headers=recep_h).json()
        assert ag["status"] == "pendente"

        resp = client.post(
            f"/agendamentos/{ag['id']}/pagamento",
            json={"valor": "50.00", "metodo": "pix"},
            headers=recep_h,
        )
        assert resp.status_code == 201
        assert float(resp.json()["valor"]) == 50.0

        ag_atualizado = client.get(f"/agendamentos/{ag['id']}", headers=recep_h).json()
        assert ag_atualizado["status"] == "confirmado"

    def test_pagamento_duplo_retorna_409(self, client, setup, recep_h):
        ag = client.post("/agendamentos/", json=_payload_agendamento(setup), headers=recep_h).json()
        client.post(f"/agendamentos/{ag['id']}/pagamento", json={"valor": "50.00", "metodo": "pix"}, headers=recep_h)
        resp = client.post(f"/agendamentos/{ag['id']}/pagamento", json={"valor": "50.00", "metodo": "pix"}, headers=recep_h)
        assert resp.status_code == 409

    def test_pagamento_em_agendamento_cancelado_retorna_422(self, client, setup, recep_h):
        ag = client.post("/agendamentos/", json=_payload_agendamento(setup), headers=recep_h).json()
        client.patch(f"/agendamentos/{ag['id']}/status", json={"status": "cancelado"}, headers=recep_h)

        resp = client.post(
            f"/agendamentos/{ag['id']}/pagamento",
            json={"valor": "50.00", "metodo": "dinheiro"},
            headers=recep_h,
        )
        assert resp.status_code == 422

    def test_recepcionista_pode_registrar_pagamento(self, client, setup, recep_h):
        ag = client.post("/agendamentos/", json=_payload_agendamento(setup), headers=recep_h).json()
        resp = client.post(
            f"/agendamentos/{ag['id']}/pagamento",
            json={"valor": "50.00", "metodo": "cartao_credito"},
            headers=recep_h,
        )
        assert resp.status_code == 201


# ---------------------------------------------------------------------------
# Listagem e filtros
# ---------------------------------------------------------------------------

class TestListarAgendamentos:
    def test_filtra_por_cliente(self, client, db, recep_h):
        c1 = criar_cliente(db, "C1")
        c2 = criar_cliente(db, "C2")
        s = criar_servico(db)
        p = criar_profissional(db)
        habilitar_servico(db, p.id, s.id)

        for cliente in [c1, c2]:
            client.post(
                "/agendamentos/",
                json={
                    "cliente_id": cliente.id,
                    "itens": [{
                        "servico_id": s.id,
                        "profissional_id": p.id,
                        "data_hora_inicio": "2027-06-01T10:00:00",
                    }],
                },
                headers=recep_h,
            )

        resp = client.get(f"/agendamentos/?cliente_id={c1.id}", headers=recep_h)
        assert resp.status_code == 200
        resultados = resp.json()
        assert all(a["cliente_id"] == c1.id for a in resultados)

    def test_filtra_por_status(self, client, setup, recep_h):
        ag = client.post("/agendamentos/", json=_payload_agendamento(setup), headers=recep_h).json()
        client.patch(f"/agendamentos/{ag['id']}/status", json={"status": "confirmado"}, headers=recep_h)

        resp = client.get("/agendamentos/?status_filtro=confirmado", headers=recep_h)
        assert all(a["status"] == "confirmado" for a in resp.json())

        resp_pendentes = client.get("/agendamentos/?status_filtro=pendente", headers=recep_h)
        assert resp_pendentes.json() == []
