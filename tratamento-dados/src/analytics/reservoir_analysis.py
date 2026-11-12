
from datetime import datetime, timezone
import math

from src.analytics.descriptive import calcular_estatisticas
from src.analytics.anomaly_detection import detectar_anomalias_iqr


def _validar_leitura(leitura):
    """Valida uma leitura individual de reservatório."""

    if not isinstance(leitura, dict):
        return False

    identificador = leitura.get("eventId")
    reservatorio = leitura.get("reservatorioId")
    timestamp = leitura.get("timestamp")
    nivel = leitura.get("nivel")
    capacidade = leitura.get("capacidade")

    if not isinstance(identificador, str) or not identificador.strip():
        return False

    if not isinstance(reservatorio, str) or not reservatorio.strip():
        return False

    if not isinstance(timestamp, str):
        return False

    try:
        data = datetime.fromisoformat(
            timestamp.replace("Z", "+00:00")
        )

        if data.tzinfo is None or data.utcoffset() is None:
            return False

    except ValueError:
        return False

    if isinstance(nivel, bool) or not isinstance(nivel, (int, float)):
        return False

    if not math.isfinite(nivel) or not 0 <= nivel <= 100:
        return False

    if isinstance(capacidade, bool) or not isinstance(capacidade, (int, float)):
        return False

    if not math.isfinite(capacidade) or capacidade <= 0:
        return False

    return True


def analisar_reservatorio(leituras):
    """
    Analisa o histórico de um reservatório.

    Calcula estatísticas descritivas, identifica outliers
    e recupera a última leitura registrada.
    """

    if not isinstance(leituras, list):
        raise ValueError("As leituras devem ser fornecidas em uma lista.")

    leituras_validas = []
    identificadores = set()

    for leitura in leituras:

        if not _validar_leitura(leitura):
            continue

        identificador = leitura["eventId"]

        if identificador in identificadores:
            continue

        identificadores.add(identificador)
        leituras_validas.append(leitura)

    if not leituras_validas:
        return None

    leituras_validas.sort(
        key=lambda leitura: datetime.fromisoformat(
            leitura["timestamp"].replace("Z", "+00:00")
        ).astimezone(timezone.utc)
    )

    niveis = [
        leitura["nivel"]
        for leitura in leituras_validas
    ]

    ultima_leitura = leituras_validas[-1]

    estatisticas = calcular_estatisticas(niveis)

    anomalias = detectar_anomalias_iqr(niveis)

    outliers = []

    for anomalia in anomalias:
        indice = anomalia["indice"]
        leitura = leituras_validas[indice]

        outliers.append({
            "eventId": leitura["eventId"],
            "timestamp": leitura["timestamp"],
            "nivel": anomalia["valor"],
            "limiteInferior": anomalia["limiteInferior"],
            "limiteSuperior": anomalia["limiteSuperior"]
        })

    return {
        "reservatorioId": ultima_leitura["reservatorioId"],
        "nivelAtual": ultima_leitura["nivel"],
        "capacidade": ultima_leitura["capacidade"],
        "ultimaAtualizacao": ultima_leitura["timestamp"],
        "quantidadeLeituras": len(leituras_validas),
        "estatisticas": estatisticas,
        "outliers": outliers
    }


def analisar_reservatorios(leituras):
    """
    Separa e analisa os históricos dos reservatórios.

    Cada reservatório recebe uma análise independente.
    """

    if not isinstance(leituras, list):
        raise ValueError("As leituras devem ser fornecidas em uma lista.")

    grupos = {}

    for leitura in leituras:

        if not _validar_leitura(leitura):
            continue

        reservatorio_id = leitura["reservatorioId"]

        if reservatorio_id not in grupos:
            grupos[reservatorio_id] = []

        grupos[reservatorio_id].append(leitura)

    resultados = {}

    for reservatorio_id, historico in grupos.items():

        resultado = analisar_reservatorio(historico)

        if resultado is not None:
            resultados[reservatorio_id] = resultado

    return resultados
