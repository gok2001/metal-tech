from datetime import datetime, timezone
import logging

from fastapi import FastAPI, HTTPException

from src.processing.validator import validar_lote
from src.analytics.production import classificar_peca, obter_minuto
from src.processing.pipeline import processar_historico
from src.storage.csv_manager import CSVManager
from src.integration.spring_boot_client import (
    SpringBootClient,
    SpringBootIntegrationError,
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="MetalTech - Ciência de Dados",
    version="1.0.0",
    description="Recepção, processamento e análise de dados industriais."
)
csv_manager = CSVManager()


def _filtrar_periodos_encerrados(processamento, agora=None):
    """Seleciona somente dados cujo minuto já foi encerrado em UTC.

    A produção ainda em andamento permanece nos CSVs e será sincronizada
    quando um lote posterior chegar e o minuto estiver encerrado.
    """
    agora = agora or datetime.now(timezone.utc)
    minuto_atual = agora.astimezone(timezone.utc).replace(
        second=0, microsecond=0
    )

    producao_fechada = []
    for registro in processamento.get("producaoPorMinuto", []):
        minuto = obter_minuto(registro.get("periodo"))
        if minuto is not None and minuto < minuto_atual:
            producao_fechada.append(registro)

    anomalias_fechadas = []
    for anomalia in processamento.get("anomalias", []):
        instante = obter_minuto(anomalia.get("data_ocorrencia"))
        if instante is not None and instante < minuto_atual:
            anomalias_fechadas.append(anomalia)

    return {
        "producaoPorMinuto": producao_fechada,
        "anomalias": anomalias_fechadas,
    }


@app.get("/health")
def health():
    return {
        "status": "UP",
        "service": "metaltech-data-processing"
    }


@app.post("/api/v1/automacao/leituras", status_code=202)
def receber_leituras(payload: dict):
    validos, invalidos, erros_lote = validar_lote(payload)

    if erros_lote:
        raise HTTPException(
            status_code=422,
            detail={
                "mensagem": "Cabeçalho do lote inválido.",
                "erros": erros_lote
            }
        )

    equipamento = payload["equipamento"]
    salvos = 0
    duplicados = 0

    # O CSV é a fonte histórica: preserva eventos brutos e inválidos.
    erros_por_indice = {
        item["indice"]: item["erros"]
        for item in invalidos
    }

    for indice, evento in enumerate(payload["leituras"]):
        evento_bruto = (
            dict(evento)
            if isinstance(evento, dict)
            else {"evento_invalido": evento}
        )
        evento_bruto.setdefault("equipamento", equipamento)

        erros_evento = list(erros_por_indice.get(indice, []))
        if (
            evento_bruto.get("tipoEvento") == "PECA_DETECTADA"
            and classificar_peca(evento_bruto) == "INCONSISTENTE"
        ):
            erros_evento.append(
                "Leitura estruturalmente válida, mas combinação "
                "dos sensores inconsistente."
            )

        salvo = csv_manager.salvar_evento(
            evento_bruto,
            erros=erros_evento or None
        )
        if salvo:
            salvos += 1
        else:
            duplicados += 1

    historico = csv_manager.listar_eventos()
    processamento = processar_historico(historico)
    dados_sincronizaveis = _filtrar_periodos_encerrados(processamento)

    # A falha do Spring Boot não invalida a recepção: os eventos já estão
    # preservados em CSV e serão reprocessados na chegada de novos lotes.
    try:
        sincronizacao = SpringBootClient().sincronizar(dados_sincronizaveis)
        status_sincronizacao = "CONCLUIDA"
    except SpringBootIntegrationError as exc:
        logger.warning(
            "Sincronização com Spring Boot pendente; histórico preservado em CSV: %s",
            exc,
        )
        sincronizacao = {
            "status": "PENDENTE",
            "motivo": "Spring Boot indisponível ou resposta inválida."
        }
        status_sincronizacao = "PENDENTE"

    return {
        "loteId": payload["loteId"],
        "status": "RECEBIDO",
        "totalRecebido": len(payload["leituras"]),
        "leiturasValidas": len(validos),
        "leiturasInvalidas": len(invalidos),
        "leiturasPersistidasCSV": salvos,
        "eventosDuplicados": duplicados,
        "recebidoEm": datetime.now(timezone.utc).isoformat(),
        "processamento": processamento,
        "sincronizacao": {
            "status": status_sincronizacao,
            "resultado": sincronizacao
        }
    }


@app.get("/api/v1/analytics/reservoirs")
def consultar_analises_reservatorios():
    """Calcula a progressão analítica a partir das 258 leituras brutas de produção.

    As quantidades acumuladas representam peças classificadas por categoria.
    Não são medições físicas de nível e não atualizam a tabela operacional
    `reservatorio` do MySQL.
    """
    historico_bruto = csv_manager.listar_eventos()
    processamento = processar_historico(historico_bruto)

    return {
        "quantidadeReservatorios": len(processamento["reservatorios"]),
        "reservatorios": processamento["reservatorios"],
        "historicoReservatorios": processamento["historicoReservatorios"],
        "histogramaReservatorios": processamento["histogramaReservatorios"],
        "origemDados": processamento["origemDadosReservatorios"],
        "metodologia": processamento["metodologiaReservatorios"],
        "geradoEm": datetime.now(timezone.utc).isoformat(),
    }
