"""Orquestra o processamento dos eventos já preservados em CSV."""

import hashlib

from src.analytics.anomaly_detection import (
    detectar_anomalias_producao,
    detectar_inconsistencias,
)
from src.analytics.production import analisar_producao, consolidar_por_minuto
from src.analytics.reservoir_analysis import analisar_reservatorios


def _gerar_id_origem(equipamento, tipo, referencia):
    """Gera chave determinística para deduplicar anomalias no backend."""
    base = f"{equipamento or 'SEM_EQUIPAMENTO'}|{tipo}|{referencia}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()[:40]


def processar_historico(eventos):
    """Gera indicadores derivados sem persistir estatísticas no banco."""
    if not isinstance(eventos, list):
        raise ValueError("O histórico deve ser uma lista de eventos.")

    eventos_pecas = [
        evento for evento in eventos
        if isinstance(evento, dict) and evento.get("tipoEvento") == "PECA_DETECTADA"
    ]
    leituras_reservatorio = [
        evento for evento in eventos
        if isinstance(evento, dict) and evento.get("tipoEvento") == "NIVEL_RESERVATORIO"
    ]

    indicadores_gerais = analisar_producao(eventos_pecas)
    producao_por_minuto = consolidar_por_minuto(eventos_pecas)
    reservatorios = analisar_reservatorios(leituras_reservatorio)

    equipamento_padrao = next((
        evento.get("equipamento") for evento in eventos
        if isinstance(evento, dict) and evento.get("equipamento")
    ), None)

    anomalias = []
    for ocorrencia in detectar_anomalias_producao(producao_por_minuto):
        anomalias.append({
            "id_origem": _gerar_id_origem(
                equipamento_padrao, "PRODUCAO_ATIPICA", ocorrencia["periodo"]
            ),
            "tipo": "PRODUCAO_ATIPICA",
            "equipamento": equipamento_padrao,
            "tipo_reservatorio": None,
            "descricao": (
                f"Produção atípica no período {ocorrencia['periodo']}: "
                f"{ocorrencia['total']} peças. Métodos: "
                f"{', '.join(ocorrencia['metodos'])}."
            ),
            "severidade": "MEDIA",
            "data_ocorrencia": ocorrencia["periodo"],
            "detalhes": ocorrencia,
        })

    for ocorrencia in detectar_inconsistencias(producao_por_minuto):
        anomalias.append({
            "id_origem": _gerar_id_origem(
                equipamento_padrao, "INCONSISTENCIA_SENSOR", ocorrencia["periodo"]
            ),
            "tipo": "INCONSISTENCIA_SENSOR",
            "equipamento": equipamento_padrao,
            "tipo_reservatorio": None,
            "descricao": ocorrencia["motivo"],
            "severidade": "BAIXA",
            "data_ocorrencia": ocorrencia["periodo"],
            "detalhes": ocorrencia,
        })

    for reservatorio_id, resultado in reservatorios.items():
        for outlier in resultado["outliers"]:
            anomalias.append({
                "tipo": "NIVEL_ATIPICO",
                "equipamento": equipamento_padrao,
                "tipo_reservatorio": reservatorio_id,
                "descricao": (
                    f"Nível atípico no reservatório {reservatorio_id}: "
                    f"{outlier['nivel']}."
                ),
                "severidade": "ALTA",
                "data_ocorrencia": outlier["timestamp"],
                "id_origem": outlier["id"],
                "detalhes": outlier,
            })

    return {
        "producao": indicadores_gerais,
        "producaoPorMinuto": producao_por_minuto,
        "reservatorios": reservatorios,
        "anomalias": anomalias,
        "totalEventosAnalisados": len(eventos),
    }
