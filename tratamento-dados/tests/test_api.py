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
