"""Histórico analítico dos reservatórios derivado da produção real.

A origem dos dados são os eventos brutos dos sensores indutivo/capacitivo.
A quantidade acumulada em cada reservatório é reconstruída pela soma das
peças classificadas em cada intervalo. Não representa medição física de
nível, percentual de capacidade ou leitura de um sensor de nível.
"""

from datetime import datetime, timezone
import math

from src.analytics.descriptive import calcular_estatisticas


def _normalizar_timestamp(valor):
    if not isinstance(valor, str):
        return None
    try:
        data = datetime.fromisoformat(valor.replace("Z", "+00:00"))
    except ValueError:
        return None
    if data.tzinfo is None or data.utcoffset() is None:
        return None
    return data.astimezone(timezone.utc)


def construir_historico_acumulado(producao_por_minuto):
    """Reconstrói a progressão acumulada por tipo de peça.

    Cada ponto representa o acumulado ao final de um minuto com eventos.
    Minutos sem eventos não são inventados nem preenchidos.
    """
    if not isinstance(producao_por_minuto, list):
        raise ValueError("A produção por minuto deve ser uma lista.")

    registros = []
    for item in producao_por_minuto:
        if not isinstance(item, dict):
            continue
        instante = _normalizar_timestamp(item.get("periodo"))
        metalicas = item.get("metalicas", 0)
        nao_metalicas = item.get("naoMetalicas", 0)
        if instante is None:
            continue
        if isinstance(metalicas, bool) or not isinstance(metalicas, (int, float)):
            continue
        if isinstance(nao_metalicas, bool) or not isinstance(nao_metalicas, (int, float)):
            continue
        if not math.isfinite(metalicas) or not math.isfinite(nao_metalicas):
            continue
        if metalicas < 0 or nao_metalicas < 0:
            continue
        registros.append((instante, int(metalicas), int(nao_metalicas)))

    registros.sort(key=lambda registro: registro[0])
    acumulado_metalico = 0
    acumulado_nao_metalico = 0
    historico = []

    for instante, metalicas, nao_metalicas in registros:
        acumulado_metalico += metalicas
        acumulado_nao_metalico += nao_metalicas
        timestamp = instante.isoformat(timespec="seconds").replace("+00:00", "Z")
        historico.append({
            "timestamp": timestamp,
            "hora": instante.strftime("%H:%M"),
            "metalicasNoIntervalo": metalicas,
            "naoMetalicasNoIntervalo": nao_metalicas,
            "acumuladoMetalico": acumulado_metalico,
            "acumuladoNaoMetalico": acumulado_nao_metalico,
        })

    return historico


def construir_histograma_acumulado(historico, quantidade_classes=10):
    """Cria classes comuns para a distribuição dos acumulados dos dois tipos."""
    if not isinstance(historico, list):
        raise ValueError("O histórico deve ser uma lista.")
    if not isinstance(quantidade_classes, int) or quantidade_classes < 1:
        raise ValueError("A quantidade de classes deve ser um inteiro positivo.")

    metalicas = [p["acumuladoMetalico"] for p in historico]
    nao_metalicas = [p["acumuladoNaoMetalico"] for p in historico]
    todos = metalicas + nao_metalicas
    if not todos:
        return []

    minimo = min(todos)
    maximo = max(todos)
    largura = (maximo - minimo) / quantidade_classes if maximo > minimo else 1.0
    classes = [
        {"frequenciaMetalica": 0, "frequenciaNaoMetalica": 0}
        for _ in range(quantidade_classes)
    ]

    for valor in metalicas:
        indice = min(int((valor - minimo) / largura), quantidade_classes - 1)
        classes[indice]["frequenciaMetalica"] += 1
    for valor in nao_metalicas:
        indice = min(int((valor - minimo) / largura), quantidade_classes - 1)
        classes[indice]["frequenciaNaoMetalica"] += 1

    resultado = []
    for indice, frequencia in enumerate(classes):
        inicio = minimo + indice * largura
        fim = maximo if indice == quantidade_classes - 1 else minimo + (indice + 1) * largura
        resultado.append({
            "inicio": round(inicio, 2),
            "fim": round(fim, 2),
            "frequenciaMetalica": frequencia["frequenciaMetalica"],
            "frequenciaNaoMetalica": frequencia["frequenciaNaoMetalica"],
        })
    return resultado


def analisar_progressao_reservatorios(producao_por_minuto):
    """Produz indicadores descritivos dos acumulados derivados da produção."""
    historico = construir_historico_acumulado(producao_por_minuto)
    histograma = construir_histograma_acumulado(historico)

    if not historico:
        return {
            "reservatorios": {},
            "historicoReservatorios": [],
            "histogramaReservatorios": [],
            "origemDados": "ACUMULO_DERIVADO_DA_PRODUCAO",
            "unidade": "pecas",
        }

    ultimo = historico[-1]
    series = {
        "METALICA": [ponto["acumuladoMetalico"] for ponto in historico],
        "NAO_METALICA": [ponto["acumuladoNaoMetalico"] for ponto in historico],
    }
    campos = {
        "METALICA": ("acumuladoMetalico", "quantidadeMetalicaAtual"),
        "NAO_METALICA": ("acumuladoNaoMetalico", "quantidadeNaoMetalicaAtual"),
    }
    reservatorios = {}
    for tipo, (campo_historico, campo_atual) in campos.items():
        reservatorios[tipo] = {
            "reservatorioId": tipo,
            campo_atual: ultimo[campo_historico],
            "ultimaAtualizacao": ultimo["timestamp"],
            "quantidadeIntervalos": len(historico),
            "unidade": "pecas",
            "estatisticas": calcular_estatisticas(series[tipo]),
        }

    return {
        "reservatorios": reservatorios,
        "historicoReservatorios": historico,
        "histogramaReservatorios": histograma,
        "origemDados": "ACUMULO_DERIVADO_DA_PRODUCAO",
        "unidade": "pecas",
        "metodologia": (
            "Acúmulo por categoria reconstruído pela soma das peças classificadas "
            "em cada intervalo de um minuto. Não representa medição física de nível "
            "nem percentual de capacidade."
        ),
    }
