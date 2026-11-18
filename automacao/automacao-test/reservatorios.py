import time
import uuid
from datetime import datetime, timezone

from config import (
    CAPACIDADE_RESERVATORIO,
    ALVO_METALICA_CM,
    ALVO_NAO_METALICA_CM,
    CONFIRMA_DIST_S,
    TEMPO_REARME_S
)


def agora_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def registrar_queda_reservatorio(estado, reservatorio_id):
    estado["contadores_reservatorio"][reservatorio_id] += 1
    qtd = estado["contadores_reservatorio"][reservatorio_id]

    nivel = round((qtd / CAPACIDADE_RESERVATORIO) * 100, 2)

    evento = {
        "id": str(uuid.uuid4()),
        "timestamp": agora_utc(),
        "tipoEvento": "NIVEL_RESERVATORIO",
        "reservatorioId": reservatorio_id,
        "nivel": nivel
    }

    with estado["trava"]:
        estado["pendentes_reservatorio"].append(evento)

    # Mantém o reset lógico do código original.
    if qtd >= CAPACIDADE_RESERVATORIO:
        estado["contadores_reservatorio"][reservatorio_id] = 0


def processar_distancia(estado, dist_cm):
    if dist_cm is None or not estado["pecas_aguardando_reservatorio"]:
        return

    proximo_destino = estado["pecas_aguardando_reservatorio"][0]

    if proximo_destino == "METALICA":
        alvo_esperado = ALVO_METALICA_CM
    else:
        alvo_esperado = ALVO_NAO_METALICA_CM

    if estado["distancia_armada"]:
        if dist_cm == alvo_esperado:
            if estado["alvo_em_confirmacao"] != alvo_esperado:
                estado["alvo_em_confirmacao"] = alvo_esperado
                estado["inicio_confirmacao"] = time.monotonic()

            elif (
                time.monotonic() - estado["inicio_confirmacao"]
                >= CONFIRMA_DIST_S
            ):
                registrar_queda_reservatorio(estado, proximo_destino)
                estado["pecas_aguardando_reservatorio"].pop(0)

                estado["distancia_armada"] = False
                estado["alvo_em_confirmacao"] = None
                estado["inicio_rearme"] = None
        else:
            estado["alvo_em_confirmacao"] = None

            # Se atingir o alvo do reservatório incorreto,
            # mantém a peça na fila sem contabilizar.
            if dist_cm in (ALVO_METALICA_CM, ALVO_NAO_METALICA_CM):
                pass
    else:
        if dist_cm not in (ALVO_METALICA_CM, ALVO_NAO_METALICA_CM):
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
