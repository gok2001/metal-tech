from src.integration.spring_boot_client import SpringBootClient


class FakeResponse:
    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload if payload is not None else []
        self.text = text
        self.ok = 200 <= status_code < 400

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        return self.responses.pop(0)


def test_envia_producao_no_contrato_spring_boot():
    session = FakeSession([FakeResponse(201)])
    client = SpringBootClient("http://localhost:8080", session=session)

    client.enviar_producao({
        "periodo": "2026-11-16T19:00:00+00:00",
        "total": 3,
        "metalicas": 2,
        "naoMetalicas": 1,
    })

    method, url, kwargs = session.calls[0]
    assert method == "POST"
    assert url.endswith("/api/v1/analytics/production")
    assert kwargs["json"] == {
        "inicio_intervalo": "2026-11-16T19:00:00+00:00",
        "total_pecas": 3,
        "pecas_metalicas": 2,
        "pecas_nao_metalicas": 1,
    }


def test_envia_anomalia_convertendo_id_origem_para_id():
    session = FakeSession([FakeResponse(201)])
    client = SpringBootClient("http://localhost:8080", session=session)
    client.enviar_anomalia({
        "id_origem": "abc123",
        "tipo": "INCONSISTENCIA_SENSOR",
        "equipamento": "ESTEIRA-01",
        "tipo_reservatorio": None,
        "descricao": "Sensor inconsistente",
        "severidade": "BAIXA",
        "data_ocorrencia": "2026-11-16T19:00:00+00:00",
    })
    payload = session.calls[0][2]["json"]
    assert payload["id"] == "abc123"
    assert "id_origem" not in payload
    assert payload["tipo_reservatorio"] is None


def test_sincronizacao_nao_reenvia_periodo_ja_registrado():
    session = FakeSession([
        FakeResponse(payload=[{"inicioIntervalo": "2026-11-16T19:00:00"}])
    ])
    client = SpringBootClient("http://localhost:8080", session=session)
    resultado = client.sincronizar({
        "producaoPorMinuto": [{
            "periodo": "2026-11-16T19:00:00+00:00",
            "total": 2,
            "metalicas": 1,
            "naoMetalicas": 1,
        }],
        "anomalias": [],
    })
    assert resultado["producoes_enviadas"] == 0
    assert resultado["producoes_ja_existentes"] == 1
    assert len(session.calls) == 1


def test_sincronizacao_envia_nova_producao_e_anomalia():
    session = FakeSession([
        FakeResponse(payload=[]),
        FakeResponse(201),
        FakeResponse(201),
    ])
    client = SpringBootClient("http://localhost:8080", session=session)
    resultado = client.sincronizar({
        "producaoPorMinuto": [{
            "periodo": "2026-11-16T19:00:00+00:00",
            "total": 2,
            "metalicas": 1,
            "naoMetalicas": 1,
        }],
        "anomalias": [{
            "id_origem": "anomalia-1",
            "tipo": "INCONSISTENCIA_SENSOR",
            "equipamento": "ESTEIRA-01",
            "tipo_reservatorio": None,
            "descricao": "Sensor inconsistente",
            "severidade": "BAIXA",
            "data_ocorrencia": "2026-11-16T19:00:00+00:00",
        }],
    })
    assert resultado["producoes_enviadas"] == 1
    assert resultado["anomalias_enviadas"] == 1
    assert len(session.calls) == 3


def test_resposta_409_de_anomalia_e_contabilizada_como_existente():
    session = FakeSession([FakeResponse(payload=[]), FakeResponse(409, text="duplicate")])
    client = SpringBootClient("http://localhost:8080", session=session)
    resultado = client.sincronizar({
        "producaoPorMinuto": [],
        "anomalias": [{
            "id_origem": "anomalia-1",
            "tipo": "INCONSISTENCIA_SENSOR",
            "equipamento": "ESTEIRA-01",
            "tipo_reservatorio": None,
            "descricao": "Sensor inconsistente",
            "severidade": "BAIXA",
            "data_ocorrencia": "2026-11-16T19:00:00+00:00",
        }],
    })
    assert resultado["anomalias_ja_existentes"] == 1
