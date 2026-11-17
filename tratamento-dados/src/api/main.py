
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException

from src.processing.validator import validar_lote
from src.analytics.production import classificar_peca
from src.analytics.reservoir_analysis import analisar_reservatorios
from src.processing.pipeline import processar_historico
from src.storage.csv_manager import CSVManager


app = FastAPI(
    title="MetalTech - Ciência de Dados",
    version="1.0.0",
    description="Recepção, processamento e análise de dados industriais."
)

csv_manager = CSVManager()


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

    # Preserva todas as leituras, inclusive as inválidas.
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

        erros_evento = list(
            erros_por_indice.get(indice, [])
        )

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

    return {
        "loteId": payload["loteId"],
        "status": "RECEBIDO",
        "totalRecebido": len(payload["leituras"]),
        "leiturasValidas": len(validos),
        "leiturasInvalidas": len(invalidos),
        "leiturasPersistidasCSV": salvos,
        "eventosDuplicados": duplicados,
        "recebidoEm": datetime.now(timezone.utc).isoformat(),
        "processamento": processamento
    }


@app.get("/api/v1/analytics/reservoirs")
def consultar_analises_reservatorios():
    """
    Recupera o histórico físico dos reservatórios
    e calcula estatísticas descritivas e outliers.
    """

    historico = csv_manager.listar_eventos()

    resultados = analisar_reservatorios(historico)

    return {
        "quantidadeReservatorios": len(resultados),
        "reservatorios": resultados,
        "geradoEm": datetime.now(timezone.utc).isoformat()
    }
