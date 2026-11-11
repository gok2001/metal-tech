
import csv
import json

from src.storage.csv_manager import CSVManager


def criar_evento():
    return {
        "id": "LEITURA-001",
        "equipamento": "ESTEIRA-01",
        "timestamp": "2026-11-11T18:00:00Z",
        "tipoEvento": "PECA_DETECTADA",
        "sensores": {
            "indutivo": True,
            "capacitivo": True
        }
    }


def obter_arquivo_leituras(diretorio):
    arquivos = list(diretorio.rglob("leituras.csv"))
    assert len(arquivos) == 1
    return arquivos[0]


def test_salvar_evento_valido(tmp_path):
    manager = CSVManager(tmp_path)

    resultado = manager.salvar_evento(criar_evento())

    assert resultado is True

    arquivo = obter_arquivo_leituras(tmp_path)

    with open(arquivo, encoding="utf-8", newline="") as f:
        registros = list(csv.DictReader(f))

    assert len(registros) == 1
    assert registros[0]["event_id"] == "LEITURA-001"


def test_salvar_evento_invalido(tmp_path):
    manager = CSVManager(tmp_path)

    evento = criar_evento()
    erros = ["Combinação inconsistente dos sensores."]

    resultado = manager.salvar_evento(evento, erros)

    assert resultado is True

    arquivos = list(tmp_path.rglob("erros.csv"))
    assert len(arquivos) == 1

    with open(arquivos[0], encoding="utf-8", newline="") as f:
        registros = list(csv.DictReader(f))

    assert len(registros) == 1
    assert "inconsistente" in registros[0]["erros"]


def test_arquivo_bruto_preserva_json_original(tmp_path):
    manager = CSVManager(tmp_path)

    evento = criar_evento()
    manager.salvar_evento(evento)

    arquivo = obter_arquivo_leituras(tmp_path)

    with open(arquivo, encoding="utf-8", newline="") as f:
        registro = next(csv.DictReader(f))

    payload = json.loads(registro["payload_json"])

    assert payload == evento


def test_nao_salvar_evento_duplicado(tmp_path):
    manager = CSVManager(tmp_path)

    evento = criar_evento()

    primeiro = manager.salvar_evento(evento)
    segundo = manager.salvar_evento(evento)

    assert primeiro is True
    assert segundo is False

    arquivo = obter_arquivo_leituras(tmp_path)

    with open(arquivo, encoding="utf-8", newline="") as f:
        registros = list(csv.DictReader(f))

    assert len(registros) == 1


def test_preservar_evento_com_timestamp_invalido(tmp_path):
    manager = CSVManager(tmp_path)

    evento = criar_evento()
    evento["timestamp"] = "data-invalida"

    resultado = manager.salvar_evento(
        evento,
        ["Timestamp inválido."]
    )

    assert resultado is True

    arquivo = obter_arquivo_leituras(tmp_path)

    with open(arquivo, encoding="utf-8", newline="") as f:
        registros = list(csv.DictReader(f))

    assert registros[0]["event_timestamp"] == "data-invalida"
