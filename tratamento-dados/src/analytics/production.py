
from collections import defaultdict
from datetime import datetime, timezone


def classificar_peca(evento):
    """
    Classifica uma peça a partir dos estados dos sensores.

    Retorna:
        METALICA
        NAO_METALICA
        SEM_PECA
        INCONSISTENTE
    """

    sensores = evento.get("sensores")

    if not isinstance(sensores, dict):
        return "INCONSISTENTE"

    indutivo = sensores.get("indutivo")
    capacitivo = sensores.get("capacitivo")

    if type(indutivo) is not bool or type(capacitivo) is not bool:
        return "INCONSISTENTE"

    if indutivo and capacitivo:
        return "METALICA"

    if not indutivo and capacitivo:
        return "NAO_METALICA"

    if not indutivo and not capacitivo:
        return "SEM_PECA"

    return "INCONSISTENTE"


def criar_indicadores(metalicas, nao_metalicas):
    """Calcula os indicadores gerais de produção."""

    total = metalicas + nao_metalicas

    percentual_metalicas = (
        (metalicas / total) * 100 if total else 0.0
    )

    percentual_nao_metalicas = (
        (nao_metalicas / total) * 100 if total else 0.0
    )

    return {
        "total": total,
        "metalicas": metalicas,
        "naoMetalicas": nao_metalicas,
        "percentualMetalicas": round(percentual_metalicas, 2),
        "percentualNaoMetalicas": round(percentual_nao_metalicas, 2)
    }


def analisar_producao(eventos):
    """
    Analisa os eventos de passagem de peças.

    Ignora eventos de outros tipos, IDs duplicados,
    eventos sem peça e combinações inconsistentes.
    """

    metalicas = 0
    nao_metalicas = 0
    inconsistentes = 0

    identificadores = set()

    for evento in eventos:

        if not isinstance(evento, dict):
            continue

        if evento.get("tipoEvento") != "PECA_DETECTADA":
            continue

        identificador = evento.get("id")

        if not isinstance(identificador, str) or not identificador.strip():
            continue

        if identificador in identificadores:
            continue

        identificadores.add(identificador)

        classificacao = classificar_peca(evento)

        if classificacao == "METALICA":
            metalicas += 1

        elif classificacao == "NAO_METALICA":
            nao_metalicas += 1

        elif classificacao == "INCONSISTENTE":
            inconsistentes += 1

    indicadores = criar_indicadores(
        metalicas,
        nao_metalicas
    )

    indicadores["inconsistentes"] = inconsistentes

    return indicadores


def obter_minuto(timestamp):
    """Converte o timestamp para o início do minuto em UTC."""

    if not isinstance(timestamp, str):
        return None

    try:
        data = datetime.fromisoformat(
            timestamp.replace("Z", "+00:00")
        )

        if data.tzinfo is None or data.utcoffset() is None:
            return None

        data = data.astimezone(timezone.utc)

        return data.replace(second=0, microsecond=0)

    except ValueError:
        return None


def consolidar_por_minuto(eventos):
    """
    Agrupa os eventos de produção por minuto.

    Retorna uma lista de indicadores cronologicamente ordenados.
    """

    grupos = defaultdict(lambda: {
        "metalicas": 0,
        "naoMetalicas": 0,
        "inconsistentes": 0,
        "identificadores": set()
    })

    for evento in eventos:

        if not isinstance(evento, dict):
            continue

        if evento.get("tipoEvento") != "PECA_DETECTADA":
            continue

        minuto = obter_minuto(evento.get("timestamp"))

        if minuto is None:
            continue

        identificador = evento.get("id")

        if not isinstance(identificador, str) or not identificador.strip():
            continue

        grupo = grupos[minuto]

        if identificador in grupo["identificadores"]:
            continue

        grupo["identificadores"].add(identificador)

        classificacao = classificar_peca(evento)

        if classificacao == "METALICA":
            grupo["metalicas"] += 1

        elif classificacao == "NAO_METALICA":
            grupo["naoMetalicas"] += 1

        elif classificacao == "INCONSISTENTE":
            grupo["inconsistentes"] += 1

    resultados = []

    for minuto in sorted(grupos):

        grupo = grupos[minuto]

        indicadores = criar_indicadores(
            grupo["metalicas"],
            grupo["naoMetalicas"]
        )

        indicadores["inconsistentes"] = grupo["inconsistentes"]

        resultados.append({
            "periodo": minuto.isoformat(),
            **indicadores
        })

    return resultados
