import requests
from datetime import datetime

IND_LIVRE = 0x7FE0
session = requests.Session()
anterior = None

def agora():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]

def ler(port):
    url = f'http://10.110.12.41/iolinkmaster/port[{port}]/iolinkdevice/pdin/getdata'
    resposta = session.get(url, timeout=0.1)
    return int(resposta.json()["data"]["value"], 16)

while True:
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