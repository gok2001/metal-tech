import json
import threading
import uuid
from datetime import datetime, timezone

import requests

from automacao.automacao_test.config import URL_API, EQUIPAMENTO, INTERVALO_ENVIO


def agora():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def agora_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def montar_payload(estado, leituras):
    estado["lote_seq"] += 1
    enviado_em = agora_utc()

    return {
        "loteId": (
            f"LOTE-{enviado_em[:10].replace('-', '')}-"
            f"{estado['lote_seq']:03d}"
        ),
        "equipamento": EQUIPAMENTO,
        "enviadoEm": enviado_em,
        "intervaloSegundos": INTERVALO_ENVIO,
        "leituras": leituras
    }


def devolver_para_fila(estado, fila, leituras):
    with estado["trava"]:
        fila[:0] = leituras


def enviar_post(estado, payload, fila):
    print("\\n========== JSON ENVIADO ==========")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print("==================================")

    try:
        resposta = requests.post(URL_API, json=payload, timeout=3)

        if resposta.status_code == 422:
            print(
                f"[{agora()}] ERRO HTTP 422 - "
                "O backend rejeitou o JSON."
            )
            print(resposta.text)
            return

        if resposta.status_code >= 500:
            print(
                f"[{agora()}] ERRO HTTP {resposta.status_code}. "
                "Eventos devolvidos para a fila."
            )
            devolver_para_fila(estado, fila, payload["leituras"])
            return

        if resposta.status_code >= 400:
            print(
                f"[{agora()}] ERRO HTTP "
                f"{resposta.status_code}: {resposta.text}"
            )
            return

        print(
            f"[{agora()}] POST enviado com sucesso: "
            f"{payload['loteId']} | HTTP {resposta.status_code} | "
            f"{len(payload['leituras'])} eventos"
        )

    except requests.exceptions.RequestException as e:
        print(f"[{agora()}] ERRO DE COMUNICAÇÃO NO POST: {e}")
        devolver_para_fila(estado, fila, payload["leituras"])


def enviar_lotes(estado):
    with estado["trava"]:
        lote_esteira = estado["pendentes_esteira"].copy()
        lote_reservatorio = estado["pendentes_reservatorio"].copy()

        estado["pendentes_esteira"].clear()
        estado["pendentes_reservatorio"].clear()

    if lote_esteira:
        payload_esteira = montar_payload(estado, lote_esteira)

        threading.Thread(
            target=enviar_post,
            args=(estado, payload_esteira, estado["pendentes_esteira"]),
            daemon=True
        ).start()

    if lote_reservatorio:
        payload_reservatorio = montar_payload(estado, lote_reservatorio)

        threading.Thread(
            target=enviar_post,
            args=(
                estado,
                payload_reservatorio,
                estado["pendentes_reservatorio"]
            ),
            daemon=True
        ).start()
