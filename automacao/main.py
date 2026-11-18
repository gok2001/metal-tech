import threading
import time

from config import INTERVALO_ENVIO, INTERVALO_LOOP
from sensores import ler
from classificacao import processar_classificacao
from reservatorios import processar_distancia
from api import enviar_lotes
from logs import registrar_erro, relatar_erros


def criar_estado():
    """Cria os estados e filas compartilhados entre os módulos."""

    return {
        # Filas dos dois POSTs
        "pendentes_esteira": [],
        "pendentes_reservatorio": [],
        "trava": threading.Lock(),
        "lote_seq": 0,

        # Contadores dos reservatórios (1 a 5)
        "contadores_reservatorio": {
            "METALICA": 0,
            "NAO_METALICA": 0,
        },

        # Controle de erros
        "erros_sensores": {
            "capacitivo/indutivo": {
                "quantidade": 0,
                "ultimo_erro": None,
            },
            "distancia": {
                "quantidade": 0,
                "ultimo_erro": None,
            },
        },
        "ultimo_relatorio_erros": time.monotonic(),

        # Estado da classificação
        "em_evento": False,
        "cap_visto": False,
        "ind_visto": False,
        "ts_evento": "",
        "ultimo_detectado": 0.0,

        # Estado do sensor de distância
        "distancia_armada": True,
        "alvo_em_confirmacao": None,
        "inicio_confirmacao": 0.0,
        "inicio_rearme": None,

        # Temporizador dos lotes
        "ultimo_envio": time.monotonic(),
    }


def main():
    estado = criar_estado()

    print("Automação da esteira iniciada.")
    print("Para encerrar, pressione Ctrl+C.")

    while True:
        # A. Relatório de erros
        relatar_erros(estado)

        agora_t = time.monotonic()

        # B. Envio dos dois lotes a cada 5 segundos
        if agora_t - estado["ultimo_envio"] >= INTERVALO_ENVIO:
            estado["ultimo_envio"] = agora_t
            enviar_lotes(estado)

        # C. Leitura do capacitivo e indutivo
        try:
            cap = ler("capacitivo")
            ind = ler("indutivo")
        except Exception as e:
            registrar_erro(estado, "capacitivo/indutivo", e)
            time.sleep(0.02)
            continue

        # D/E. Detecção e classificação
        processar_classificacao(estado, cap, ind)

        # F. Leitura independente da distância
        dist_cm = None
        try:
            dist_raw = ler("distancia")
            dist_cm = dist_raw // 16
        except Exception as e:
            registrar_erro(estado, "distancia", e)

        # G. Controle dos reservatórios
        processar_distancia(estado, dist_cm)

        # H. Pequena pausa do loop
        time.sleep(INTERVALO_LOOP)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAutomação encerrada pelo usuário.")