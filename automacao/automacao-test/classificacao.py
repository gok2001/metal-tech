import time
import uuid
from datetime import datetime, timezone

from config import FIM_EVENTO, IND_LIVRE


def agora_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def adicionar_evento_peca(estado, tipo, ts, indutivo, capacitivo):
    leitura = {
        "id": str(uuid.uuid4()),
        "timestamp": ts,
        "tipoEvento": tipo,
        "sensores": {
            "indutivo": indutivo,
            "capacitivo": capacitivo
        }
    }

    with estado["trava"]:
        estado["pendentes_esteira"].append(leitura)


def processar_classificacao(estado, cap, ind):
    capacitivo = (cap & 1) == 1
    indutivo = ind != IND_LIVRE

    agora_t = time.monotonic()
    detectando = capacitivo or indutivo

    if detectando:
        if not estado["em_evento"]:
            estado["em_evento"] = True
            estado["ts_evento"] = agora_utc()
            estado["cap_visto"] = False
            estado["ind_visto"] = False

        estado["ultimo_detectado"] = agora_t
        estado["cap_visto"] = estado["cap_visto"] or capacitivo
        estado["ind_visto"] = estado["ind_visto"] or indutivo

    if (
        estado["em_evento"]
        and not detectando
        and agora_t - estado["ultimo_detectado"] >= FIM_EVENTO
    ):
        classificacao = (
            "METALICA" if estado["ind_visto"]
            else "NAO_METALICA"
        )

        adicionar_evento_peca(
            estado,
            "PECA_DETECTADA",
            estado["ts_evento"],
            estado["ind_visto"],
            estado["cap_visto"]
        )

        estado["pecas_aguardando_reservatorio"].append(classificacao)

        adicionar_evento_peca(
            estado,
            "SEM_PECA",
            agora_utc(),
            False,
            False
        )

        estado["em_evento"] = False
        estado["cap_visto"] = False
        estado["ind_visto"] = False
