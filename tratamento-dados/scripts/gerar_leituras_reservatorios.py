#!/usr/bin/env python3
"""Gera leituras DIDÁTICAS de reservatórios usando o período da produção existente.

- Não altera nem apaga os CSVs existentes.
- Usa o endpoint oficial POST /api/v1/automacao/leituras.
- Marca cada evento com origemDado='SIMULADO'.
- Os valores são unidades numéricas fictícias, não percentuais nem medidas físicas.

Execute a partir de tratamento-dados/scripts ou coloque este arquivo em
tratamento-dados/scripts/ e execute: python scripts/gerar_leituras_reservatorios.py
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests


INTERVALO_SEGUNDOS = 5
EQUIPAMENTO = "ESTEIRA-01"
RESERVATORIOS = {
    "METALICA": {"incremento": 0.92, "limite_simulado": 185.0, "reinicio": 9.0},
    "NAO_METALICA": {"incremento": 0.68, "limite_simulado": 165.0, "reinicio": 7.0},
}


def parse_timestamp(value: str) -> datetime | None:
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None or dt.utcoffset() is None:
            return None
        return dt.astimezone(timezone.utc)
    except (AttributeError, TypeError, ValueError):
        return None


def localizar_inicio_e_niveis(data_raw: Path) -> tuple[datetime, dict[str, float]]:
    """Usa as últimas leituras dos reservatórios como ponto inicial.

    Se ainda não houver leituras de reservatório, usa o último evento de
    produção como referência temporal e níveis iniciais didáticos.
    """
    ultimas_leituras: dict[str, tuple[datetime, float]] = {}
    ultimo_evento_producao: datetime | None = None

    for arquivo in data_raw.glob("**/leituras.csv"):
        with arquivo.open("r", newline="", encoding="utf-8") as f:
            for linha in csv.DictReader(f):
                try:
                    evento = json.loads(linha.get("payload_json") or "{}")
                except json.JSONDecodeError:
                    continue
                if not isinstance(evento, dict):
                    continue
                instante = parse_timestamp(evento.get("timestamp"))
                if not instante:
                    continue
                if evento.get("tipoEvento") in {"PECA_DETECTADA", "SEM_PECA"}:
                    if ultimo_evento_producao is None or instante > ultimo_evento_producao:
                        ultimo_evento_producao = instante
                if evento.get("tipoEvento") == "NIVEL_RESERVATORIO":
                    rid = evento.get("reservatorioId")
                    nivel = evento.get("nivel")
                    if rid in RESERVATORIOS and isinstance(nivel, (int, float)) and not isinstance(nivel, bool):
                        atual = ultimas_leituras.get(rid)
                        if atual is None or instante > atual[0]:
                            ultimas_leituras[rid] = (instante, float(nivel))

    niveis_iniciais = {"METALICA": 24.0, "NAO_METALICA": 18.0}
    if ultimas_leituras:
        inicio = max(item[0] for item in ultimas_leituras.values())
        for rid, (_, nivel) in ultimas_leituras.items():
            niveis_iniciais[rid] = nivel
        return inicio, niveis_iniciais

    if ultimo_evento_producao is None:
        raise RuntimeError(
            f"Nenhum evento de produção ou reservatório com timestamp válido foi encontrado em {data_raw}."
        )
    return ultimo_evento_producao, niveis_iniciais


def gerar_eventos(inicio: datetime, fim: datetime, niveis_iniciais: dict[str, float]) -> list[dict]:
    eventos: list[dict] = []
    niveis = dict(niveis_iniciais)
    amostra = 0
    instante = inicio.replace(microsecond=0)

    while instante <= fim:
        for reservatorio_id, cfg in RESERVATORIOS.items():
            # Oscilação determinística e suave, apenas para demonstrar variação.
            oscilacao = 0.18 * math.sin(amostra / 5.0)
            nivel = niveis[reservatorio_id] + cfg["incremento"] + oscilacao

            # Representa a troca automática como reinício do nível simulado.
            if nivel >= cfg["limite_simulado"]:
                nivel = cfg["reinicio"]

            niveis[reservatorio_id] = round(nivel, 2)
            eventos.append({
                "id": f"SIM-{reservatorio_id}-{uuid.uuid4().hex}",
                "timestamp": instante.isoformat().replace("+00:00", "Z"),
                "tipoEvento": "NIVEL_RESERVATORIO",
                "reservatorioId": reservatorio_id,
                "nivel": niveis[reservatorio_id],
                "origemDado": "SIMULADO",
            })
        instante += timedelta(seconds=INTERVALO_SEGUNDOS)
        amostra += 1

    return eventos


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Gera e salva o JSON, mas não envia para a API."
    )
    parser.add_argument(
        "--api", default=os.getenv("METALTECH_API_URL", "http://localhost:8000"),
        help="URL base da API Python (padrão: http://localhost:8000)."
    )
    args = parser.parse_args()

    # Espera que o arquivo esteja em tratamento-dados/scripts/.
    raiz_tratamento = Path(__file__).resolve().parents[1]
    data_raw = raiz_tratamento / "data" / "raw"
    data_simulada = raiz_tratamento / "data" / "simulated"
    data_simulada.mkdir(parents=True, exist_ok=True)

    inicio, niveis_iniciais = localizar_inicio_e_niveis(data_raw)
    agora = datetime.now(timezone.utc).replace(microsecond=0)
    fim = agora - timedelta(seconds=agora.second % INTERVALO_SEGUNDOS)
    if fim <= inicio:
        raise RuntimeError("A última leitura existente é posterior ao horário atual; não há período para simular.")
    inicio_geracao = inicio + timedelta(seconds=INTERVALO_SEGUNDOS)
    leituras = gerar_eventos(inicio_geracao, fim, niveis_iniciais)
    lote = {
        "loteId": f"LOTE-SIM-RES-{agora.strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}",
        "equipamento": EQUIPAMENTO,
        "enviadoEm": agora.isoformat().replace("+00:00", "Z"),
        "intervaloSegundos": INTERVALO_SEGUNDOS,
        "leituras": leituras,
    }

    nome = f"leituras_reservatorios_simuladas_{agora.strftime('%Y%m%dT%H%M%SZ')}.json"
    caminho_json = data_simulada / nome
    caminho_json.write_text(json.dumps(lote, ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== GERAÇÃO DE LEITURAS SIMULADAS ===")
    print(f"Período simulado após a última leitura existente: {inicio_geracao.isoformat()} até {fim.isoformat()}")
    print(f"Intervalo: {INTERVALO_SEGUNDOS} segundos")
    print(f"Leituras geradas: {len(leituras)} ({len(leituras)//2} por reservatório)")
    print("Origem: SIMULADO — valores numéricos fictícios, sem unidade física definida.")
    print(f"Arquivo preservado: {caminho_json}")

    if args.dry_run:
        print("Modo dry-run: nada foi enviado à API.")
        return 0

    url = args.api.rstrip("/") + "/api/v1/automacao/leituras"
    try:
        resposta = requests.post(url, json=lote, timeout=60)
        print(f"Resposta da API: HTTP {resposta.status_code}")
        print(resposta.text[:12000])
        resposta.raise_for_status()
    except requests.RequestException as exc:
        print(f"Falha no envio: {exc}")
        print("O JSON foi mantido em data/simulated; não foi apagado.")
        return 1

    print("Envio concluído. Consulte GET /api/v1/analytics/reservoirs no Swagger.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
