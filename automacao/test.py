import json
import threading
import time
import uuid
from datetime import datetime, timezone

import requests

URL_API = "http://10.110.12.57:8000/api/v1/automacao/leituras"  # troque pelo endereço real
API = "http://10.110.12.76:5000"  # endereço da API; troque pelo IP do PC dela se rodar em outro PC

EQUIPAMENTO = "ESTEIRA-01"
INTERVALO_ENVIO = 5       # segundos entre envios
FIM_EVENTO = 0.3          # segundos sem detecção para encerrar uma peça
JANELA_IND = 0.6          # segundos que espera o indutivo depois que o evento começa
IND_LIVRE = 0x7FE0

CAPACIDADE_RESERVATORIO = 5
ALVO_METALICA_CM = 7.0
ALVO_NAO_METALICA_CM = 15.0
TOLERANCIA_CM = 1.5
FATOR_CM = 0.1            # ajuste conforme averiguação do sensor (ex.: 0.1 se hex vier em mm, 1.0 se vier em cm)

session = requests.Session()
pendentes = []
trava = threading.Lock()
lote_seq = 0
anterior = None
ultima_dist_cm = None

contadores_reservatorio = {
    "METALICA": 0,
    "NAO_METALICA": 0,
}


def agora():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def agora_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ler(nome):
    url = f"{API}/sensores/{nome}"
    resposta = session.get(url, timeout=0.1)
    resposta.raise_for_status()
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
    # por enquanto também imprime o JSON no terminal
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def enviar_post(leituras, payload):
    try:
        resposta = requests.post(URL_API, json=payload, timeout=3)
        resposta.raise_for_status()
        print(f"[{agora()}] Enviado {payload['loteId']} ({len(leituras)} leituras)")
    except Exception as e:
        print(f"[{agora()}] Falha no envio: {e}")
        with trava:
            pendentes[:0] = leituras  # devolve para a fila e tenta no próximo envio


def adicionar_evento_peca(tipo, ts, indutivo, capacitivo):
    leitura = {
        "id": str(uuid.uuid4()),
        "timestamp": ts,
        "tipoEvento": tipo,
        "sensores": {"indutivo": indutivo, "capacitivo": capacitivo},
    }
    with trava:
        pendentes.append(leitura)


def registrar_queda_reservatorio(reservatorio_id):
    contadores_reservatorio[reservatorio_id] += 1
    qtd = contadores_reservatorio[reservatorio_id]
    nivel = round((qtd / CAPACIDADE_RESERVATORIO) * 100.0, 2)

    evento_nivel = {
        "id": str(uuid.uuid4()),
        "timestamp": agora_utc(),
        "tipoEvento": "NIVEL_RESERVATORIO",
        "reservatorioId": reservatorio_id,
        "nivel": nivel,
    }
    with trava:
        pendentes.append(evento_nivel)

    print(f"[{agora()}] Reservatório {reservatorio_id}: {qtd}/{CAPACIDADE_RESERVATORIO} peças -> nível {nivel}%")

    if qtd >= CAPACIDADE_RESERVATORIO:
        contadores_reservatorio[reservatorio_id] = 0
        print(f"[{agora()}] Reservatório {reservatorio_id} atingiu 100% e resetou automaticamente para 0.")


em_evento = False
decidido = False
cap_visto = False
ind_visto = False
ts_evento = ""
inicio_evento = 0.0
ultimo_detectado = 0.0
ultimo_envio = time.monotonic()

# peça aguardando chegar ao seu respectivo reservatório (7 cm metálica / 15 cm não metálica)
peca_aguardando_reservatorio = None

while True:
    # 1) hora de enviar o lote?
    if time.monotonic() - ultimo_envio >= INTERVALO_ENVIO:
        ultimo_envio = time.monotonic()
        with trava:
            lote = pendentes.copy()
            pendentes.clear()
        payload = montar_payload(lote)
        enviar(payload)

        if lote:
            threading.Thread(target=enviar_post, args=(lote, payload), daemon=True).start()

    # 2) leitura dos sensores
    try:
        cap = ler("capacitivo")
        ind = ler("indutivo")
        dist_raw = ler("distancia")
    except Exception as e:
        print(f"[{agora()}] Erro: {e}")
        continue

    capacitivo = (cap & 1) == 1
    indutivo = ind != IND_LIVRE
    dist_cm = round(dist_raw * FATOR_CM, 2)
    estado = (capacitivo, indutivo)

    if estado != anterior:
        print(f"[{agora()}] Capacitivo: {capacitivo} ({cap:04X}) | Indutivo: {indutivo} ({ind:04X})")
        anterior = estado

    if dist_cm != ultima_dist_cm:
        print(f"[{agora()}] Distância: {dist_cm:.2f} cm (raw: {dist_raw:04X})")
        ultima_dist_cm = dist_cm

    # 3) agrupa as detecções em eventos (uma peça = um evento)
    agora_t = time.monotonic()
    detectando = capacitivo or indutivo

    if detectando:
        if not em_evento:
            em_evento = True
            decidido = False
            ts_evento = agora_utc()
            inicio_evento = agora_t
            cap_visto = False
            ind_visto = False
        ultimo_detectado = agora_t
        cap_visto = cap_visto or capacitivo
        ind_visto = ind_visto or indutivo

    # decide: o indutivo apareceu (metálica) ou a janela acabou sem ele (não metálica)
    if em_evento and not decidido and (ind_visto or agora_t - inicio_evento >= JANELA_IND):
        adicionar_evento_peca("PECA_DETECTADA", ts_evento, ind_visto, cap_visto)
        peca_aguardando_reservatorio = "METALICA" if ind_visto else "NAO_METALICA"
        decidido = True

    # fecha o evento quando os dois sensores ficam livres por FIM_EVENTO
    if em_evento and not detectando and agora_t - ultimo_detectado >= FIM_EVENTO:
        if not decidido:
            adicionar_evento_peca("PECA_DETECTADA", ts_evento, ind_visto, cap_visto)
            if peca_aguardando_reservatorio is None:
                peca_aguardando_reservatorio = "METALICA" if ind_visto else "NAO_METALICA"
        adicionar_evento_peca("SEM_PECA", agora_utc(), False, False)
        em_evento = False

    # 4) verifica chegada da peça ao reservatório pelo sensor de distância
    if peca_aguardando_reservatorio is not None:
        if peca_aguardando_reservatorio == "METALICA":
            bateu_alvo = abs(dist_cm - ALVO_METALICA_CM) <= TOLERANCIA_CM
        else:
            bateu_alvo = abs(dist_cm - ALVO_NAO_METALICA_CM) <= TOLERANCIA_CM

        if bateu_alvo:
            registrar_queda_reservatorio(peca_aguardando_reservatorio)
            peca_aguardando_reservatorio = None