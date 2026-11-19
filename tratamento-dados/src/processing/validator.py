from datetime import datetime
TIPOS_EVENTO = {"PECA_DETECTADA", "SEM_PECA"}


def validar_timestamp(timestamp):
    if not isinstance(timestamp, str) or not timestamp.strip():
        return False
    try:
        data = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return data.tzinfo is not None and data.utcoffset() is not None
    except ValueError:
        return False


def validar_evento(evento, equipamento=None, permitir_inconsistencia=False):
    """Valida um evento individual do contrato Automação -> Ciência de Dados."""
    erros = []
    if not isinstance(evento, dict):
        return False, ["O evento deve ser um objeto JSON."]

    identificador = evento.get("id")
    if not isinstance(identificador, str) or not identificador.strip():
        erros.append("Identificador ausente ou inválido.")

    equipamento_evento = evento.get("equipamento", equipamento)
    if not isinstance(equipamento_evento, str) or not equipamento_evento.strip():
        erros.append("Equipamento ausente ou inválido.")

    if not validar_timestamp(evento.get("timestamp")):
        erros.append("Timestamp inválido ou sem fuso horário.")

    tipo = evento.get("tipoEvento")
    if tipo not in TIPOS_EVENTO:
        erros.append("Tipo de evento desconhecido.")
    elif tipo in {"PECA_DETECTADA", "SEM_PECA"}:
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
            if tipo == "SEM_PECA" and not (indutivo is False and capacitivo is False):
                erros.append("Evento SEM_PECA exige os dois sensores inativos.")
            if (tipo == "PECA_DETECTADA" and not permitir_inconsistencia
                    and type(indutivo) is bool and type(capacitivo) is bool
                    and indutivo and not capacitivo):
                erros.append("Combinação inconsistente: indutivo ativo e capacitivo inativo.")

    return not erros, erros


def validar_lote(lote):
    """Valida cabeçalho e eventos; equipamento é herdado do lote."""
    erros_lote = []
    if not isinstance(lote, dict):
        return [], [{"indice": None, "id": None, "erros": ["O lote deve ser um objeto JSON."]}], erros_lote

    lote_id = lote.get("loteId")
    equipamento = lote.get("equipamento")
    enviado_em = lote.get("enviadoEm")
    intervalo = lote.get("intervaloSegundos")
    leituras = lote.get("leituras")

    if not isinstance(lote_id, str) or not lote_id.strip():
        erros_lote.append("loteId ausente ou inválido.")
    if not isinstance(equipamento, str) or not equipamento.strip():
        erros_lote.append("equipamento ausente ou inválido.")
    if not validar_timestamp(enviado_em):
        erros_lote.append("enviadoEm inválido ou sem fuso horário.")
    if isinstance(intervalo, bool) or not isinstance(intervalo, int) or intervalo <= 0:
        erros_lote.append("intervaloSegundos deve ser inteiro positivo.")
    if not isinstance(leituras, list):
        erros_lote.append("leituras deve ser uma lista.")

    if erros_lote:
        return [], [{"indice": None, "id": None, "erros": erros_lote}], erros_lote

    validos, invalidos = [], []
    ids = set()
    for indice, evento in enumerate(leituras):
        aprovado, erros = validar_evento(evento, equipamento=equipamento, permitir_inconsistencia=True)
        event_id = evento.get("id") if isinstance(evento, dict) else None
        if aprovado and event_id in ids:
            aprovado = False
            erros.append("Identificador duplicado dentro do lote.")
        if aprovado:
            ids.add(event_id)
            normalizado = dict(evento)
            normalizado["equipamento"] = equipamento
            validos.append(normalizado)
        else:
            invalidos.append({"indice": indice, "id": event_id, "erros": erros})
    return validos, invalidos, []


def validar_eventos(eventos):
    """Compatibilidade com a validação de listas utilizada pelos testes antigos."""
    validos, invalidos = [], []
    identificadores = set()
    if not isinstance(eventos, list):
        return [], [{"indice": None, "id": None, "erros": ["A entrada deve ser uma lista de eventos."]}]
    for indice, evento in enumerate(eventos):
        aprovado, erros = validar_evento(evento)
        identificador = evento.get("id") if isinstance(evento, dict) else None
        if aprovado and identificador in identificadores:
            aprovado = False
            erros.append("Identificador duplicado.")
        if aprovado:
            identificadores.add(identificador)
            validos.append(evento)
        else:
            invalidos.append({"indice": indice, "id": identificador, "erros": erros})
    return validos, invalidos
