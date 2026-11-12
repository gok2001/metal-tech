
from src.analytics.production import (
    classificar_peca,
    analisar_producao,
    consolidar_por_minuto
)


def criar_evento(
    identificador,
    indutivo,
    capacitivo,
    timestamp="2026-11-12T18:00:00Z"
):
    return {
        "id": identificador,
        "equipamento": "ESTEIRA-01",
        "timestamp": timestamp,
        "tipoEvento": "PECA_DETECTADA",
        "sensores": {
            "indutivo": indutivo,
            "capacitivo": capacitivo
        }
    }


def test_classificar_peca_metalica():
    evento = criar_evento("001", True, True)

    assert classificar_peca(evento) == "METALICA"


def test_classificar_peca_nao_metalica():
    evento = criar_evento("002", False, True)

    assert classificar_peca(evento) == "NAO_METALICA"


def test_identificar_ausencia_de_peca():
    evento = criar_evento("003", False, False)

    assert classificar_peca(evento) == "SEM_PECA"


def test_identificar_combinacao_inconsistente():
    evento = criar_evento("004", True, False)

    assert classificar_peca(evento) == "INCONSISTENTE"


def test_calcular_indicadores_de_producao():
    eventos = [
        criar_evento("001", True, True),
        criar_evento("002", True, True),
        criar_evento("003", False, True),
        criar_evento("004", False, True)
    ]

    resultado = analisar_producao(eventos)

    assert resultado["total"] == 4
    assert resultado["metalicas"] == 2
    assert resultado["naoMetalicas"] == 2
    assert resultado["percentualMetalicas"] == 50.0
    assert resultado["percentualNaoMetalicas"] == 50.0


def test_ignorar_eventos_duplicados():
    evento = criar_evento("001", True, True)

    resultado = analisar_producao([
        evento,
        evento
    ])

    assert resultado["total"] == 1


def test_contabilizar_eventos_inconsistentes():
    eventos = [
        criar_evento("001", True, False),
        criar_evento("002", True, True)
    ]

    resultado = analisar_producao(eventos)

    assert resultado["total"] == 1
    assert resultado["inconsistentes"] == 1


def test_ignorar_eventos_de_reservatorio():
    evento = {
        "id": "005",
        "tipoEvento": "NIVEL_RESERVATORIO",
        "nivelReservatorio": 80
    }

    resultado = analisar_producao([evento])

    assert resultado["total"] == 0


def test_consolidar_producao_por_minuto():
    eventos = [
        criar_evento(
            "001", True, True,
            "2026-11-12T18:00:10Z"
        ),
        criar_evento(
            "002", False, True,
            "2026-11-12T18:00:30Z"
        ),
        criar_evento(
            "003", True, True,
            "2026-11-12T18:01:10Z"
        )
    ]

    resultado = consolidar_por_minuto(eventos)

    assert len(resultado) == 2

    assert resultado[0]["total"] == 2
    assert resultado[0]["metalicas"] == 1
    assert resultado[0]["naoMetalicas"] == 1

    assert resultado[1]["total"] == 1
    assert resultado[1]["metalicas"] == 1


def test_consolidar_eventos_com_timestamps_diferentes():
    eventos = [
        criar_evento(
            "001", True, True,
            "2026-11-12T21:00:10-03:00"
        ),
        criar_evento(
            "002", False, True,
            "2026-11-13T00:00:40Z"
        )
    ]

    resultado = consolidar_por_minuto(eventos)

    assert len(resultado) == 1
    assert resultado[0]["total"] == 2


def test_ignorar_timestamp_invalido_na_consolidacao():
    evento = criar_evento(
        "001",
        True,
        True,
        "data-invalida"
    )

    resultado = consolidar_por_minuto([evento])

    assert resultado == []
