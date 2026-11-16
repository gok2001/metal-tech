
import json
import random
import uuid

from datetime import datetime, timedelta, timezone
from pathlib import Path


EQUIPAMENTO = "ESTEIRA-01"

TOTAL_PECAS = 120
INTERVALO_SEGUNDOS = 3

CAPACIDADE_MAXIMA = 100.0

PERCENTUAL_METALICAS = 0.60
PROBABILIDADE_ANOMALIA = 0.05


def gerar_id():
    return str(uuid.uuid4())


def gerar_timestamp(inicio, segundos):
    momento = inicio + timedelta(seconds=segundos)

    return momento.isoformat().replace("+00:00", "Z")


def gerar_evento_peca(timestamp):
    metalica = random.random() < PERCENTUAL_METALICAS

    indutivo = True if metalica else False
    capacitivo = True

    # Introdução controlada de inconsistências
    if random.random() < PROBABILIDADE_ANOMALIA:
        indutivo = True
        capacitivo = False

    return {
        "id": gerar_id(),
        "equipamento": EQUIPAMENTO,
        "timestamp": timestamp,
        "tipoEvento": "PECA_DETECTADA",
        "sensores": {
            "indutivo": indutivo,
            "capacitivo": capacitivo
        }
    }


def gerar_evento_reservatorio(timestamp, nivel):
    return {
        "id": gerar_id(),
        "equipamento": EQUIPAMENTO,
        "timestamp": timestamp,
        "tipoEvento": "NIVEL_RESERVATORIO",
        "nivelReservatorio": round(nivel, 2)
    }


def gerar_dados():
    eventos = []

    inicio = datetime.now(timezone.utc)

    nivel = 20.0

    for i in range(TOTAL_PECAS):

        segundos = i * INTERVALO_SEGUNDOS

        timestamp = gerar_timestamp(inicio, segundos)

        # Evento de passagem da peça
        eventos.append(
            gerar_evento_peca(timestamp)
        )

        # Atualização gradual do reservatório
        nivel += random.uniform(0.3, 0.8)

        # Anomalias de nível controladas
        if random.random() < PROBABILIDADE_ANOMALIA:
            nivel += random.uniform(5, 12)

        nivel = min(nivel, CAPACIDADE_MAXIMA)

        # Uma medição de reservatório a cada 10 segundos
        if i % 3 == 0:
            eventos.append(
                gerar_evento_reservatorio(
                    timestamp,
                    nivel
                )
            )

    # Ordenar todos os eventos cronologicamente
    eventos.sort(key=lambda evento: evento["timestamp"])

    return eventos


def salvar_json(eventos):
    raiz_projeto = Path(__file__).resolve().parents[2]

    caminho = (
        raiz_projeto /
        "data" /
        "samples" /
        "leituras_exemplo.json"
    )

    caminho.parent.mkdir(parents=True, exist_ok=True)

    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(
            eventos,
            arquivo,
            indent=4,
            ensure_ascii=False
        )

    print(f"Dados gerados: {len(eventos)} eventos")
    print(f"Arquivo salvo em: {caminho}")


def main():
    eventos = gerar_dados()
    salvar_json(eventos)


if __name__ == "__main__":
    main()
