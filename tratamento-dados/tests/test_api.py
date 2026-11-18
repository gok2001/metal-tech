from fastapi.testclient import TestClient
from src.api.main import app, csv_manager


def test_health():
    client = TestClient(app)
    assert client.get("/health").json()["status"] == "UP"


def test_receber_lote_com_eventos_validos_e_inconsistentes(tmp_path, monkeypatch):
    from src.api import main
    monkeypatch.setattr(main, "csv_manager", __import__("src.storage.csv_manager", fromlist=["CSVManager"]).CSVManager(tmp_path))
    client = TestClient(app)
    lote = {
        "loteId": "LOTE-001",
        "equipamento": "ESTEIRA-01",
        "enviadoEm": "2026-11-14T10:00:05Z",
        "intervaloSegundos": 5,
        "leituras": [
            {"id": "EV-001", "timestamp": "2026-11-14T10:00:01Z",
             "tipoEvento": "PECA_DETECTADA",
             "sensores": {"indutivo": True, "capacitivo": True}},
            {"id": "EV-002", "timestamp": "2026-11-14T10:00:02Z",
             "tipoEvento": "PECA_DETECTADA",
             "sensores": {"indutivo": True, "capacitivo": False}},
            {"id": "EV-003", "timestamp": "2026-11-14T10:00:03Z",
             "tipoEvento": "NIVEL_RESERVATORIO",
             "reservatorioId": "METALICA", "nivel": 12.7}
        ]
    }
    response = client.post("/api/v1/automacao/leituras", json=lote)
    assert response.status_code == 202
    data = response.json()
    assert data["leiturasValidas"] == 3
    assert data["leiturasInvalidas"] == 0
    assert data["leiturasPersistidasCSV"] == 3
    processamento = data["processamento"]
    assert processamento["producao"]["total"] == 1
    assert processamento["producao"]["metalicas"] == 1
    assert processamento["producao"]["inconsistentes"] == 1
    assert processamento["reservatorios"]["METALICA"]["nivelAtual"] == 12.7


def test_rejeitar_cabecalho_invalido():
    client = TestClient(app)
    response = client.post("/api/v1/automacao/leituras", json={"leituras": []})
    assert response.status_code == 422


def test_filtrar_periodos_encerrados_nao_envia_minuto_atual():
    from datetime import datetime, timezone
    from src.api.main import _filtrar_periodos_encerrados

    processamento = {
        "producaoPorMinuto": [
            {"periodo": "2026-11-17T20:00:00+00:00", "total": 2},
            {"periodo": "2026-11-17T20:01:00+00:00", "total": 1},
        ],
        "anomalias": [
            {"data_ocorrencia": "2026-11-17T20:00:30+00:00", "id_origem": "a"},
            {"data_ocorrencia": "2026-11-17T20:01:10+00:00", "id_origem": "b"},
        ],
    }

    resultado = _filtrar_periodos_encerrados(
        processamento,
        agora=datetime(2026, 11, 17, 20, 1, 20, tzinfo=timezone.utc),
    )

    assert [item["periodo"] for item in resultado["producaoPorMinuto"]] == [
        "2026-11-17T20:00:00+00:00"
    ]
    assert [item["id_origem"] for item in resultado["anomalias"]] == ["a"]


def test_receber_lote_dispara_sincronizacao_apenas_dados_processados(
    tmp_path, monkeypatch
):
    from src import api
    from src.storage.csv_manager import CSVManager

    chamadas = []

    class ClienteFake:
        def sincronizar(self, dados):
            chamadas.append(dados)
            return {
                "producoes_enviadas": 1,
                "producoes_ja_existentes": 0,
                "anomalias_enviadas": 0,
                "anomalias_ja_existentes": 0,
            }

    monkeypatch.setattr(api.main, "csv_manager", CSVManager(tmp_path))
    monkeypatch.setattr(api.main, "SpringBootClient", ClienteFake)

    lote = {
        "loteId": "LOTE-AUTO-001",
        "equipamento": "ESTEIRA-01",
        "enviadoEm": "2026-11-14T10:02:05Z",
        "intervaloSegundos": 5,
        "leituras": [
            {
                "id": "AUTO-001",
                "timestamp": "2026-11-14T10:00:01Z",
                "tipoEvento": "PECA_DETECTADA",
                "sensores": {"indutivo": True, "capacitivo": True},
            }
        ],
    }

    response = TestClient(api.main.app).post(
        "/api/v1/automacao/leituras", json=lote
    )

    assert response.status_code == 202
    assert response.json()["sincronizacao"]["status"] == "CONCLUIDA"
    assert len(chamadas) == 1
    assert "producaoPorMinuto" in chamadas[0]
    assert "anomalias" in chamadas[0]
    assert "leituras" not in chamadas[0]
