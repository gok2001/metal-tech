import json
import threading
import time
import uuid
from datetime import datetime, timezone

import requests

# URL_API = "http://SEU-SERVIDOR/api/v1/automacao/leituras"  # troque pelo endereço real
EQUIPAMENTO = "ESTEIRA-01"
INTERVALO_ENVIO = 5   # segundos entre envios
FIM_EVENTO = 0.3      # segundos sem detecção para encerrar uma peça
IND_LIVRE = 0x7FE0

session = requests.Session()
pendentes = []
trava = threading.Lock()
lote_seq = 0
anterior = None


def agora():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def agora_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ler(port):
    url = f'http://10.110.12.41/iolinkmaster/port[{port}]/iolinkdevice/pdin/getdata'
    resposta = session.get(url, timeout=0.1)
    return int(resposta.json()["data"]["value"], 16)


def montar_payload(leituras):
    global lote_seq
    lote_seq += 1
    enviado_em = agora_utc()
    return {
        "loteId": f"LOTE-{enviado_em[:10].replace('-', '')}-{lote_seq:03d}",
        "equipamento": EQUIPAMENTO,
        "enviadoEm": enviado_em,
        "intervaloSegundos": INTERVALO_ENVIO,
        "leituras": leituras,
    }


def enviar(payload):
    # por enquanto só imprime o JSON no terminal
    print(json.dumps(payload, indent=2, ensure_ascii=False))


# def enviar_post(leituras, payload):
#     try:
#         resposta = requests.post(URL_API, json=payload, timeout=3)
#         resposta.raise_for_status()
#         print(f"[{agora()}] Enviado {payload['loteId']} ({len(leituras)} leituras)")
#     except Exception as e:
#         print(f"[{agora()}] Falha no envio: {e}")
#         with trava:
#             pendentes[:0] = leituras  # devolve para a fila e tenta no próximo envio


em_evento = False
cap_visto = ind_visto = False
ts_evento = ""
ultimo_detectado = 0.0
ultimo_envio = time.monotonic()

while True:
    # 1) hora de enviar o lote?
    if time.monotonic() - ultimo_envio >= INTERVALO_ENVIO:
        ultimo_envio = time.monotonic()
        with trava:
            lote = pendentes.copy()
            pendentes.clear()
        payload = montar_payload(lote)
        enviar(payload)
        # POST: descomente quando o servidor estiver pronto
        # if lote:
        #     threading.Thread(target=enviar_post, args=(lote, payload), daemon=True).start()

    # 2) leitura dos sensores
    try:
        cap = ler(2)
        ind = ler(3)
    except Exception as e:
        print(f"[{agora()}] Erro: {e}")
        continue

    capacitivo = (cap & 1) == 1
    indutivo = ind != IND_LIVRE
    estado = (capacitivo, indutivo)

    if estado != anterior:
        print(f"[{agora()}] Capacitivo: {capacitivo} ({cap:04X}) | Indutivo: {indutivo} ({ind:04X})")
        anterior = estado

    # 3) agrupa as detecções em eventos (uma peça = um evento)
    agora_t = time.monotonic()
    if capacitivo or indutivo:
        if not em_evento:
            em_evento = True
            ts_evento = agora_utc()
            cap_visto = ind_visto = False
        ultimo_detectado = agora_t
        cap_visto = cap_visto or capacitivo
        ind_visto = ind_visto or indutivo
    elif em_evento and agora_t - ultimo_detectado >= FIM_EVENTO:
        leitura = {
            "id": str(uuid.uuid4()),
            "timestamp": ts_evento,
            "tipoEvento": "PECA_DETECTADA",
            "sensores": {"indutivo": ind_visto, "capacitivo": cap_visto},
        }
        sem_peca = {
            "id": str(uuid.uuid4()),
            "timestamp": agora_utc(),
            "tipoEvento": "SEM_PECA",
            "sensores": {"indutivo": False, "capacitivo": False},
        }
        with trava:
            pendentes.append(leitura)
            pendentes.append(sem_peca)
        em_evento = False