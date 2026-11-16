import requests

BASE = "http://10.110.12.41/iolinkmaster/port[{}]/iolinkdevice/pdin/getdata"

LIMIAR_CAP = 0x0400   # capacitivo acima disso = tem peça
IND_LIVRE = 0x7FE0    # indutivo sem detecção
CICLOS_FIM = 3        # ciclos livres seguidos para encerrar a passagem

session = requests.Session()

def ler(porta):
    r = session.get(BASE.format(porta), timeout=0.1)
    return int(r.json()["data"]["value"], 16)

em_peca = False
metal = False
livres = 0
total_metal = 0
total_nao_metal = 0
pico_cap = 0
ind_visto = IND_LIVRE

while True:
    try:
        cap = ler(2)
        ind = ler(3)
    except Exception as e:
        print(f"")
        session.close()
        session = requests.Session()
        continue

    if cap > LIMIAR_CAP or ind != IND_LIVRE:
        if not em_peca:
            pico_cap = 0
            ind_visto = IND_LIVRE
        em_peca = True
        livres = 0
        pico_cap = max(pico_cap, cap)
        if ind != IND_LIVRE:
            metal = True
            ind_visto = ind
    elif em_peca:
        livres += 1
        if livres >= CICLOS_FIM:
            if metal:
                total_metal += 1
            else:
                total_nao_metal += 1
            tipo = "METAL" if metal else "NAO METAL"
            print(f"{tipo} | cap pico: {pico_cap:04X} | ind: {ind_visto:04X} "
                  f"| Metálicas: {total_metal} | Não metálicas: {total_nao_metal}")
            em_peca = False
            metal = False