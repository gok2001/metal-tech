
import pytest

from src.analytics.anomaly_detection import (
    detectar_anomalias_iqr,
    detectar_anomalias_desvio_padrao,
    detectar_anomalias_producao,
    detectar_inconsistencias
)


def test_identificar_anomalia_com_iqr():
    valores = [10, 11, 12, 10, 11, 12, 10, 100]

    resultado = detectar_anomalias_iqr(valores)

    assert len(resultado) == 1
    assert resultado[0]["valor"] == 100


def test_nao_identificar_anomalia_em_serie_regular():
    valores = [10, 11, 12, 10, 11, 12, 10, 11]

    resultado = detectar_anomalias_iqr(valores)

    assert resultado == []


def test_iqr_exigir_quatro_observacoes():
    valores = [10, 11, 12]

    resultado = detectar_anomalias_iqr(valores)

    assert resultado == []


def test_identificar_anomalia_por_desvio_padrao():
    valores = [10, 11, 12, 10, 11, 12, 10, 100]

    resultado = detectar_anomalias_desvio_padrao(
        valores,
        limite=2.0
    )

    assert len(resultado) == 1
    assert resultado[0]["valor"] == 100


def test_nao_identificar_anomalia_em_serie_constante():
    valores = [10, 10, 10, 10, 10]

    resultado = detectar_anomalias_desvio_padrao(valores)

    assert resultado == []


def test_detectar_anomalias_na_producao():
    producao = [
        {"periodo": "18:00", "total": 10},
        {"periodo": "18:01", "total": 11},
        {"periodo": "18:02", "total": 12},
        {"periodo": "18:03", "total": 10},
        {"periodo": "18:04", "total": 11},
        {"periodo": "18:05", "total": 12},
        {"periodo": "18:06", "total": 10},
        {"periodo": "18:07", "total": 100}
    ]

    resultado = detectar_anomalias_producao(producao)

    assert len(resultado) == 1
    assert resultado[0]["total"] == 100
    assert resultado[0]["periodo"] == "18:07"


def test_combinar_metodos_de_deteccao():
    producao = [
        {"periodo": f"18:0{i}", "total": valor}
        for i, valor in enumerate(
            [10, 11, 12, 10, 11, 12, 10, 100]
        )
    ]

    resultado = detectar_anomalias_producao(
        producao,
        limite_desvio=2.0
    )

    assert len(resultado) == 1
    assert "IQR" in resultado[0]["metodos"]
    assert "DESVIO_PADRAO" in resultado[0]["metodos"]


def test_identificar_inconsistencias_dos_sensores():
    producao = [
        {
            "periodo": "18:00",
            "total": 10,
            "inconsistentes": 2
        },
        {
            "periodo": "18:01",
            "total": 12,
            "inconsistentes": 0
        }
    ]

    resultado = detectar_inconsistencias(producao)

    assert len(resultado) == 1
    assert resultado[0]["quantidade"] == 2
    assert resultado[0]["tipo"] == "INCONSISTENCIA_SENSOR"


def test_ignorar_registros_invalidos():
    producao = [
        {"periodo": "18:00", "total": 10},
        {"periodo": "18:01", "total": None},
        {"periodo": "18:02", "total": "invalido"},
        {"periodo": "18:03", "total": 12}
    ]

    resultado = detectar_anomalias_producao(producao)

    assert resultado == []


def test_rejeitar_entrada_nula():
    with pytest.raises(ValueError):
        detectar_anomalias_producao(None)


def test_rejeitar_fator_iqr_invalido():
    with pytest.raises(ValueError):
        detectar_anomalias_iqr([1, 2, 3, 4], fator=0)


def test_rejeitar_limite_desvio_invalido():
    with pytest.raises(ValueError):
        detectar_anomalias_desvio_padrao(
            [1, 2, 3],
            limite=0
        )
