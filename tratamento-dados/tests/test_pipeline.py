from src.processing.pipeline import processar_historico


def test_processar_historico_consolida_producao_e_reservatorios():
    eventos = [
        {
            "id": "P-1", "equipamento": "ESTEIRA-01",
            "timestamp": "2026-11-16T19:00:01Z",
            "tipoEvento": "PECA_DETECTADA",
            "sensores": {"indutivo": True, "capacitivo": True},
        },
        {
            "id": "P-2", "equipamento": "ESTEIRA-01",
            "timestamp": "2026-11-16T19:00:20Z",
            "tipoEvento": "PECA_DETECTADA",
            "sensores": {"indutivo": False, "capacitivo": True},
        },
        {
            "id": "P-3", "equipamento": "ESTEIRA-01",
            "timestamp": "2026-11-16T19:00:30Z",
            "tipoEvento": "PECA_DETECTADA",
            "sensores": {"indutivo": True, "capacitivo": False},
        },
        {
            "id": "R-1", "equipamento": "ESTEIRA-01",
            "timestamp": "2026-11-16T19:00:35Z",
            "tipoEvento": "NIVEL_RESERVATORIO",
            "reservatorioId": "METALICA", "nivel": 135.5,
        },
    ]

    resultado = processar_historico(eventos)

    assert resultado["producao"]["total"] == 2
    assert resultado["producao"]["metalicas"] == 1
    assert resultado["producao"]["naoMetalicas"] == 1
    assert resultado["producao"]["inconsistentes"] == 1
    assert len(resultado["producaoPorMinuto"]) == 1
    assert resultado["producaoPorMinuto"][0]["total"] == 2
    assert resultado["reservatorios"]["METALICA"]["nivelAtual"] == 135.5
    assert resultado["totalEventosAnalisados"] == 4
    assert any(a["tipo"] == "INCONSISTENCIA_SENSOR" for a in resultado["anomalias"])


def test_processar_historico_vazio():
    resultado = processar_historico([])

    assert resultado["producao"]["total"] == 0
    assert resultado["producaoPorMinuto"] == []
    assert resultado["reservatorios"] == {}
    assert resultado["anomalias"] == []
