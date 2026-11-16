
import pytest

from src.analytics.reservoir_analysis import (
    analisar_reservatorio,
    analisar_reservatorios,
)


def criar_leitura(
    event_id,
    reservatorio_id,
    nivel,
    timestamp
):
    return {
        "eventId": event_id,
        "reservatorioId": reservatorio_id,
        "timestamp": timestamp,
        "nivel": nivel,
        "capacidade": 100
    }


def test_analisar_historico_de_reservatorio():
    leituras = [
        criar_leitura(
            "001", "RES-01", 20,
            "2026-11-12T18:00:00Z"
        ),
        criar_leitura(
            "002", "RES-01", 40,
            "2026-11-12T18:01:00Z"
        ),
        criar_leitura(
            "003", "RES-01", 60,
            "2026-11-12T18:02:00Z"
        )
    ]

    resultado = analisar_reservatorio(leituras)

    assert resultado["reservatorioId"] == "RES-01"
    assert resultado["quantidadeLeituras"] == 3
    assert resultado["nivelAtual"] == 60
    assert resultado["estatisticas"]["media"] == 40


def test_calcular_estatisticas_do_reservatorio():
    leituras = [
        criar_leitura(
            str(i), "RES-01", nivel,
            f"2026-11-12T18:0{i}:00Z"
        )
        for i, nivel in enumerate([20, 40, 60, 80])
    ]

    resultado = analisar_reservatorio(leituras)

    estatisticas = resultado["estatisticas"]

    assert estatisticas["media"] == 50
    assert estatisticas["mediana"] == 50
    assert estatisticas["minimo"] == 20
    assert estatisticas["maximo"] == 80


def test_identificar_nivel_atual_pela_leitura_mais_recente():
    leituras = [
        criar_leitura(
            "001", "RES-01", 80,
            "2026-11-12T18:02:00Z"
        ),
        criar_leitura(
            "002", "RES-01", 30,
            "2026-11-12T18:00:00Z"
        )
    ]

    resultado = analisar_reservatorio(leituras)

    assert resultado["nivelAtual"] == 80
    assert resultado["ultimaAtualizacao"] == "2026-11-12T18:02:00Z"


def test_separar_dois_reservatorios():
    leituras = [
        criar_leitura(
            "001", "RES-01", 30,
            "2026-11-12T18:00:00Z"
        ),
        criar_leitura(
            "002", "RES-02", 70,
            "2026-11-12T18:00:00Z"
        )
    ]

    resultado = analisar_reservatorios(leituras)

    assert len(resultado) == 2
    assert resultado["RES-01"]["nivelAtual"] == 30
    assert resultado["RES-02"]["nivelAtual"] == 70


def test_ignorar_leitura_duplicada():
    leitura = criar_leitura(
        "001", "RES-01", 50,
        "2026-11-12T18:00:00Z"
    )

    resultado = analisar_reservatorio([
        leitura,
        leitura
    ])

    assert resultado["quantidadeLeituras"] == 1


def test_ignorar_nivel_invalido():
    leituras = [
        criar_leitura(
            "001", "RES-01", 50,
            "2026-11-12T18:00:00Z"
        ),
        criar_leitura(
            "002", "RES-01", 101,
            "2026-11-12T18:01:00Z"
        ),
        criar_leitura(
            "003", "RES-01", -1,
            "2026-11-12T18:02:00Z"
        )
    ]

    resultado = analisar_reservatorio(leituras)

    assert resultado["quantidadeLeituras"] == 1
    assert resultado["nivelAtual"] == 50


def test_ignorar_timestamp_sem_fuso():
    leituras = [
        criar_leitura(
            "001", "RES-01", 50,
            "2026-11-12T18:00:00"
        )
    ]

    resultado = analisar_reservatorios(leituras)

    assert resultado == {}


def test_identificar_outlier_no_historico():
    niveis = [20, 21, 22, 20, 21, 22, 20, 95]

    leituras = [
        criar_leitura(
            str(i), "RES-01", nivel,
            f"2026-11-12T18:0{i}:00Z"
        )
        for i, nivel in enumerate(niveis)
    ]

    resultado = analisar_reservatorio(leituras)

    assert len(resultado["outliers"]) == 1
    assert resultado["outliers"][0]["nivel"] == 95


def test_retornar_none_sem_leituras_validas():
    resultado = analisar_reservatorio([
        {"eventId": "001", "nivel": 50}
    ])

    assert resultado is None


def test_rejeitar_entrada_que_nao_seja_lista():
    with pytest.raises(ValueError):
        analisar_reservatorios(None)
