from src.processing.validator import validar_eventos


def test_validar_eventos_dos_sensores_de_producao():
    eventos = [
        {
            "id": "TESTE-METALICA",
            "equipamento": "ESTEIRA-01",
            "timestamp": "2026-11-18T00:54:34Z",
            "tipoEvento": "PECA_DETECTADA",
            "sensores": {"indutivo": True, "capacitivo": True},
        },
        {
            "id": "TESTE-NAO-METALICA",
            "equipamento": "ESTEIRA-01",
            "timestamp": "2026-11-18T00:54:40Z",
            "tipoEvento": "PECA_DETECTADA",
            "sensores": {"indutivo": False, "capacitivo": True},
        },
        {
            "id": "TESTE-SEM-PECA",
            "equipamento": "ESTEIRA-01",
            "timestamp": "2026-11-18T00:54:45Z",
            "tipoEvento": "SEM_PECA",
            "sensores": {"indutivo": False, "capacitivo": False},
        },
    ]

    validos, invalidos = validar_eventos(eventos)

    assert len(validos) == 3
    assert invalidos == []
