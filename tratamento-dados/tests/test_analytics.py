
import pytest

from src.analytics.descriptive import (
    calcular_estatisticas,
    analisar_producao
)


def test_calcular_media_mediana_e_moda():
    valores = [2, 4, 4, 4, 5, 5, 7, 9]

    resultado = calcular_estatisticas(valores)

    assert resultado["media"] == 5.0
    assert resultado["mediana"] == 4.5
    assert resultado["moda"] == [4.0]


def test_calcular_variancia_e_desvio_padrao():
    valores = [2, 4, 4, 4, 5, 5, 7, 9]

    resultado = calcular_estatisticas(valores)

    assert resultado["variancia"] == 4.0
    assert resultado["desvioPadrao"] == 2.0


def test_calcular_quartis():
    valores = [2, 4, 4, 4, 5, 5, 7, 9]

    resultado = calcular_estatisticas(valores)

    assert resultado["quartis"]["q1"] == 4.0
    assert resultado["quartis"]["q2"] == 4.5
    assert resultado["quartis"]["q3"] == 5.5


def test_calcular_minimo_e_maximo():
    valores = [2, 4, 4, 4, 5, 5, 7, 9]

    resultado = calcular_estatisticas(valores)

    assert resultado["minimo"] == 2.0
    assert resultado["maximo"] == 9.0


def test_identificar_multiplas_modas():
    valores = [1, 1, 2, 2, 3]

    resultado = calcular_estatisticas(valores)

    assert resultado["moda"] == [1.0, 2.0]


def test_ignorar_valores_invalidos():
    valores = [10, 20, None, "inválido", float("nan")]

    resultado = calcular_estatisticas(valores)

    assert resultado["quantidade"] == 2
    assert resultado["media"] == 15.0


def test_retornar_vazio_sem_valores_validos():
    resultado = calcular_estatisticas([None, "inválido", float("nan")])

    assert resultado["quantidade"] == 0
    assert resultado["media"] is None
    assert resultado["moda"] == []


def test_rejeitar_serie_nula():
    with pytest.raises(ValueError):
        calcular_estatisticas(None)


def test_analisar_categorias_de_producao():
    producao = {
        "total": [10, 12, 15],
        "metalicas": [6, 7, 9],
        "naoMetalicas": [4, 5, 6]
    }

    resultado = analisar_producao(producao)

    assert resultado["total"]["media"] == 12.333333333333334
    assert resultado["metalicas"]["media"] == pytest.approx(7.3333333333)
    assert resultado["naoMetalicas"]["media"] == 5.0
