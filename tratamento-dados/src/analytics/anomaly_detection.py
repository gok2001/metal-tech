
import math

import numpy as np


def _validar_serie(valores):
    """Converte e valida uma série numérica."""

    if valores is None:
        raise ValueError("A série não pode ser nula.")

    resultado = []

    for valor in valores:
        if isinstance(valor, bool):
            continue

        try:
            numero = float(valor)

            if math.isfinite(numero):
                resultado.append(numero)

        except (TypeError, ValueError):
            continue

    return resultado


def detectar_anomalias_iqr(valores, fator=1.5):
    """
    Identifica valores discrepantes utilizando o método IQR.

    Valores abaixo de Q1 - 1.5 * IQR ou acima de
    Q3 + 1.5 * IQR são considerados atípicos.
    """

    serie = _validar_serie(valores)

    if len(serie) < 4:
        return []

    if fator <= 0:
        raise ValueError("O fator IQR deve ser positivo.")

    q1 = float(np.percentile(serie, 25))
    q3 = float(np.percentile(serie, 75))

    intervalo = q3 - q1

    limite_inferior = q1 - fator * intervalo
    limite_superior = q3 + fator * intervalo

    anomalias = []

    for indice, valor in enumerate(serie):

        if valor < limite_inferior or valor > limite_superior:
            anomalias.append({
                "indice": indice,
                "valor": valor,
                "limiteInferior": float(limite_inferior),
                "limiteSuperior": float(limite_superior)
            })

    return anomalias


def detectar_anomalias_desvio_padrao(valores, limite=3.0):
    """
    Identifica valores com distância superior ao limite
    de desvios padrão em relação à média.
    """

    serie = _validar_serie(valores)

    if len(serie) < 2:
        return []

    if limite <= 0:
        raise ValueError("O limite deve ser positivo.")

    media = float(np.mean(serie))
    desvio = float(np.std(serie, ddof=0))

    if desvio == 0:
        return []

    anomalias = []

    for indice, valor in enumerate(serie):

        z_score = abs(valor - media) / desvio

        if z_score > limite:
            anomalias.append({
                "indice": indice,
                "valor": valor,
                "zScore": float(z_score),
                "media": media,
                "desvioPadrao": desvio
            })

    return anomalias


def detectar_anomalias_producao(
    producao_por_minuto,
    fator_iqr=1.5,
    limite_desvio=3.0
):
    """
    Analisa a produção consolidada por minuto.

    Retorna os períodos identificados como atípicos,
    informando quais métodos detectaram a ocorrência.
    """

    if not isinstance(producao_por_minuto, list):
        raise ValueError("A produção deve ser uma lista.")

    valores = []
    periodos = []

    for registro in producao_por_minuto:

        if not isinstance(registro, dict):
            continue

        total = registro.get("total")
        periodo = registro.get("periodo")

        if isinstance(total, bool):
            continue

        try:
            total = float(total)

            if not math.isfinite(total) or total < 0:
                continue

        except (TypeError, ValueError):
            continue

        valores.append(total)
        periodos.append(periodo)

    anomalias_iqr = detectar_anomalias_iqr(
        valores,
        fator_iqr
    )

    anomalias_desvio = detectar_anomalias_desvio_padrao(
        valores,
        limite_desvio
    )

    ocorrencias = {}

    for anomalia in anomalias_iqr:

        indice = anomalia["indice"]

        ocorrencias[indice] = {
            "periodo": periodos[indice],
            "total": valores[indice],
            "metodos": [],
            "motivos": []
        }

        ocorrencias[indice]["metodos"].append("IQR")

        ocorrencias[indice]["motivos"].append(
            "Produção fora dos limites do intervalo interquartil."
        )

    for anomalia in anomalias_desvio:

        indice = anomalia["indice"]

        if indice not in ocorrencias:
            ocorrencias[indice] = {
                "periodo": periodos[indice],
                "total": valores[indice],
                "metodos": [],
                "motivos": []
            }

        ocorrencias[indice]["metodos"].append("DESVIO_PADRAO")

        ocorrencias[indice]["motivos"].append(
            "Produção distante da média em desvios padrão."
        )

    return [
        ocorrencias[indice]
        for indice in sorted(ocorrencias)
    ]


def detectar_inconsistencias(producao_por_minuto):
    """
    Identifica períodos que apresentam eventos
    com combinações inconsistentes dos sensores.
    """

    if not isinstance(producao_por_minuto, list):
        raise ValueError("A produção deve ser uma lista.")

    ocorrencias = []

    for registro in producao_por_minuto:

        if not isinstance(registro, dict):
            continue

        inconsistentes = registro.get("inconsistentes", 0)

        if (
            isinstance(inconsistentes, bool)
            or not isinstance(inconsistentes, (int, float))
            or not math.isfinite(inconsistentes)
            or inconsistentes <= 0
        ):
            continue

        ocorrencias.append({
            "periodo": registro.get("periodo"),
            "quantidade": inconsistentes,
            "tipo": "INCONSISTENCIA_SENSOR",
            "motivo": "Foram identificadas combinações inconsistentes dos sensores."
        })

    return ocorrencias
