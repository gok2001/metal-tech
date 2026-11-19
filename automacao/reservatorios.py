import time
import uuid
from datetime import datetime, timezone

from config import (
    CAPACIDADE_RESERVATORIO,
    ALVO_METALICA_CM,
    ALVO_NAO_METALICA_CM,
    TOLERANCIA_DIST,
    CONFIRMA_DIST_S,
    TEMPO_REARME_S,
)


def agora_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def identificar_reservatorio(dist_cm):
    if abs(dist_cm - ALVO_METALICA_CM) <= TOLERANCIA_DIST:
        return "METALICA"
    if abs(dist_cm - ALVO_NAO_METALICA_CM) <= TOLERANCIA_DIST:
        return "NAO_METALICA"
    return None


def registrar_queda_reservatorio(estado, reservatorio_id):
    estado["contadores_reservatorio"][reservatorio_id] += 1
    qtd = estado["contadores_reservatorio"][reservatorio_id]

    evento = {
        "id": str(uuid.uuid4()),
        "timestamp": agora_utc(),
        "tipoEvento": "NIVEL_RESERVATORIO",
        "reservatorioId": reservatorio_id,
        "nivel": qtd,
    }

    with estado["trava"]:
        estado["pendentes_reservatorio"].append(evento)

    if qtd >= CAPACIDADE_RESERVATORIO:
        estado["contadores_reservatorio"][reservatorio_id] = 0


def processar_distancia(estado, dist_cm):
    if dist_cm is None:
        return

    reservatorio_detectado = identificar_reservatorio(dist_cm)

    if estado["distancia_armada"]:
        if reservatorio_detectado is not None:
            if estado["alvo_em_confirmacao"] != reservatorio_detectado:
                estado["alvo_em_confirmacao"] = reservatorio_detectado
                estado["inicio_confirmacao"] = time.monotonic()
            elif (
                time.monotonic() - estado["inicio_confirmacao"]
                >= CONFIRMA_DIST_S
            ):
                registrar_queda_reservatorio(estado, reservatorio_detectado)
                estado["distancia_armada"] = False
                estado["alvo_em_confirmacao"] = None
                estado["inicio_rearme"] = None
        else:
            estado["alvo_em_confirmacao"] = None
    else:
        if reservatorio_detectado is None:
            if estado["inicio_rearme"] is None:
                estado["inicio_rearme"] = time.monotonic()
            elif (
                time.monotonic() - estado["inicio_rearme"]
                >= TEMPO_REARME_S
            ):
                estado["distancia_armada"] = True
                estado["inicio_rearme"] = None
        else:
            estado["inicio_rearme"] = None