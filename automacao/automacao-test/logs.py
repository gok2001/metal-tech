import time

from config import INTERVALO_RELATORIO_ERROS
from api import agora


def registrar_erro(estado, sensor, erro):
    estado["erros_sensores"][sensor]["quantidade"] += 1
    estado["erros_sensores"][sensor]["ultimo_erro"] = str(erro)


def relatar_erros(estado):
    agora_t = time.monotonic()

    if agora_t - estado["ultimo_relatorio_erros"] < INTERVALO_RELATORIO_ERROS:
        return

    estado["ultimo_relatorio_erros"] = agora_t

    for sensor, dados in estado["erros_sensores"].items():
        quantidade = dados["quantidade"]

        if quantidade > 0:
            print(
                f"\\n[{agora()}] ERRO - Sensor {sensor}: "
                f"{quantidade} falhas nos últimos "
                f"{INTERVALO_RELATORIO_ERROS} segundos."
            )
            print(f"Último erro: {dados['ultimo_erro']}")

            dados["quantidade"] = 0
            dados["ultimo_erro"] = None
