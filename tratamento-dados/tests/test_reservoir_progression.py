from src.analytics.reservoir_progression import (
    analisar_progressao_reservatorios,
    construir_historico_acumulado,
    construir_histograma_acumulado,
)


def test_progressao_acumula_cada_categoria_independentemente():
    producao = [
        {"periodo": "2026-11-18T00:54:00+00:00", "metalicas": 1, "naoMetalicas": 4},
        {"periodo": "2026-11-18T00:55:00+00:00", "metalicas": 2, "naoMetalicas": 6},
    ]

    historico = construir_historico_acumulado(producao)

    assert historico[0]["acumuladoMetalico"] == 1
    assert historico[0]["acumuladoNaoMetalico"] == 4
    assert historico[1]["acumuladoMetalico"] == 3
    assert historico[1]["acumuladoNaoMetalico"] == 10
    assert historico[1]["hora"] == "00:55"


def test_histograma_contabiliza_os_pontos_de_ambas_as_series():
    historico = [
        {"acumuladoMetalico": 1, "acumuladoNaoMetalico": 4},
        {"acumuladoMetalico": 3, "acumuladoNaoMetalico": 10},
        {"acumuladoMetalico": 5, "acumuladoNaoMetalico": 12},
    ]

    histograma = construir_histograma_acumulado(historico, quantidade_classes=4)

    assert sum(item["frequenciaMetalica"] for item in histograma) == 3
    assert sum(item["frequenciaNaoMetalica"] for item in histograma) == 3


def test_estatisticas_usam_as_21_observacoes_acumuladas():
    producao = [
        {"periodo": f"2026-11-18T00:{minuto:02d}:00+00:00", "metalicas": 1, "naoMetalicas": 2}
        for minuto in range(21)
    ]

    resultado = analisar_progressao_reservatorios(producao)

    assert resultado["reservatorios"]["METALICA"]["quantidadeMetalicaAtual"] == 21
    assert resultado["reservatorios"]["NAO_METALICA"]["quantidadeNaoMetalicaAtual"] == 42
    assert resultado["reservatorios"]["METALICA"]["quantidadeIntervalos"] == 21
    assert resultado["reservatorios"]["METALICA"]["estatisticas"]["quantidade"] == 21
    assert len(resultado["historicoReservatorios"]) == 21
    assert len(resultado["histogramaReservatorios"]) == 10


def test_ignora_minutos_invalidos_sem_inventar_pontos():
    historico = construir_historico_acumulado([
        {"periodo": "2026-11-18T00:54:00+00:00", "metalicas": 1, "naoMetalicas": 4},
        {"periodo": "2026-11-18T00:55:00", "metalicas": 5, "naoMetalicas": 5},
        {"periodo": "2026-11-18T00:56:00+00:00", "metalicas": -1, "naoMetalicas": 1},
    ])

    assert len(historico) == 1
    assert historico[0]["acumuladoMetalico"] == 1
