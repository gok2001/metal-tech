
from datetime import datetime
from math import isfinite


TIPOS_EVENTO = {
    "PECA_DETECTADA",
    "NIVEL_RESERVATORIO"
}


def validar_timestamp(timestamp):
    """Verifica se a data possui formato válido e fuso horário."""

    if not isinstance(timestamp, str) or not timestamp.strip():
        return False

    try:
        data = datetime.fromisoformat(
            timestamp.replace("Z", "+00:00")
        )

        return data.tzinfo is not None and data.utcoffset() is not None

    except ValueError:
        return False


def validar_evento(evento):
    """Valida individualmente um evento recebido."""

    erros = []

    if not isinstance(evento, dict):
        return False, ["O evento deve ser um objeto JSON."]

    # Identificador
    identificador = evento.get("id")

    if not isinstance(identificador, str) or not identificador.strip():
        erros.append("Identificador ausente ou inválido.")

    # Equipamento
    equipamento = evento.get("equipamento")

    if not isinstance(equipamento, str) or not equipamento.strip():
        erros.append("Equipamento ausente ou inválido.")

    # Timestamp
    if not validar_timestamp(evento.get("timestamp")):
        erros.append("Timestamp inválido ou sem fuso horário.")

    # Tipo de evento
    tipo_evento = evento.get("tipoEvento")

    if tipo_evento not in TIPOS_EVENTO:
        erros.append("Tipo de evento desconhecido.")

    elif tipo_evento == "PECA_DETECTADA":

        sensores = evento.get("sensores")

        if not isinstance(sensores, dict):
            erros.append("Objeto de sensores ausente ou inválido.")

        else:
            indutivo = sensores.get("indutivo")
            capacitivo = sensores.get("capacitivo")

            if type(indutivo) is not bool:
                erros.append("Sensor indutivo deve possuir valor booleano.")

            if type(capacitivo) is not bool:
                erros.append("Sensor capacitivo deve possuir valor booleano.")

            if (
                type(indutivo) is bool
                and type(capacitivo) is bool
                and indutivo
                and not capacitivo
            ):
                erros.append(
                    "Combinação inconsistente: indutivo ativo "
                    "e capacitivo inativo."
                )

    elif tipo_evento == "NIVEL_RESERVATORIO":

        nivel = evento.get("nivelReservatorio")

        if isinstance(nivel, bool) or not isinstance(nivel, (int, float)):
            erros.append("Nível do reservatório deve ser numérico.")

        elif not isfinite(nivel) or not 0 <= nivel <= 100:
            erros.append(
                "Nível do reservatório deve estar entre 0% e 100%."
            )

    return len(erros) == 0, erros


def validar_eventos(eventos):
    """
    Valida uma coleção de eventos.

    Retorna:
    - lista de eventos válidos;
    - lista de registros inválidos com seus respectivos erros.
    """

    validos = []
    invalidos = []

    identificadores = set()

    if not isinstance(eventos, list):
        return [], [{
            "indice": None,
            "id": None,
            "erros": ["A entrada deve ser uma lista de eventos."]
        }]

    for indice, evento in enumerate(eventos):

        aprovado, erros = validar_evento(evento)

        identificador = (
            evento.get("id")
            if isinstance(evento, dict)
            else None
        )

        if aprovado and identificador in identificadores:
            aprovado = False
            erros.append("Identificador duplicado.")

        if aprovado:
            identificadores.add(identificador)
            validos.append(evento)

        else:
            invalidos.append({
                "indice": indice,
                "id": identificador,
                "erros": erros
            })

    return validos, invalidos
