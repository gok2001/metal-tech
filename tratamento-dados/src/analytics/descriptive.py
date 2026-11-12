
import math

import pandas as pd


def calcular_estatisticas(valores):
    """
    Calcula estatísticas descritivas de uma série numérica.

    Parâmetro:
        valores: lista ou série de valores numéricos.

    Retorno:
        Dicionário com medidas estatísticas.
    """

    if valores is None:
        raise ValueError("A série de valores não pode ser nula.")

    serie = pd.Series(valores)

    # Converter para valores numéricos
    serie = pd.to_numeric(serie, errors="coerce")

    # Remover valores inválidos e infinitos
    serie = serie.dropna()
    serie = serie[
        serie.map(lambda valor: math.isfinite(float(valor)))
    ]

    if serie.empty:
        return {
            "quantidade": 0,
            "media": None,
            "mediana": None,
            "moda": [],
            "variancia": None,
            "desvioPadrao": None,
            "quartis": {
                "q1": None,
                "q2": None,
                "q3": None
            },
            "minimo": None,
            "maximo": None
        }

    modas = serie.mode().tolist()

    return {
        "quantidade": int(serie.count()),

        "media": float(serie.mean()),

        "mediana": float(serie.median()),

        "moda": [float(valor) for valor in modas],

        "variancia": float(serie.var(ddof=0)),

        "desvioPadrao": float(serie.std(ddof=0)),

        "quartis": {
            "q1": float(serie.quantile(0.25)),
            "q2": float(serie.quantile(0.50)),
            "q3": float(serie.quantile(0.75))
        },

        "minimo": float(serie.min()),

        "maximo": float(serie.max())
    }


def analisar_producao(producao):
    """
    Calcula estatísticas separadas por classificação.

    Parâmetro esperado:
        {
            "total": [10, 12, 15],
            "metalicas": [6, 7, 9],
            "naoMetalicas": [4, 5, 6]
        }
    """

    resultado = {}

    for categoria, valores in producao.items():
        resultado[categoria] = calcular_estatisticas(valores)

    return resultado
