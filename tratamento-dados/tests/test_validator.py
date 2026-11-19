import pytest

from src.processing.validator import validar_evento, validar_eventos


def criar_evento_peca():
    return {
        "id": "LEITURA-001",
        "equipamento": "ESTEIRA-01",
        "timestamp": "2026-11-11T18:00:00Z",
        "tipoEvento": "PECA_DETECTADA",
        "sensores": {"indutivo": True, "capacitivo": True},
    }


def criar_evento_sem_peca():
    return {
        "id": "LEITURA-002",
        "equipamento": "ESTEIRA-01",
        "timestamp": "2026-11-11T18:00:05Z",
        "tipoEvento": "SEM_PECA",
        "sensores": {"indutivo": False, "capacitivo": False},
    }


def test_validar_peca_metalica():
    aprovado, erros = validar_evento(criar_evento_peca())
    assert aprovado is True
    assert erros == []


def test_validar_peca_nao_metalica():
    evento = criar_evento_peca()
    evento["sensores"]["indutivo"] = False
    aprovado, erros = validar_evento(evento)
    assert aprovado is True
    assert erros == []


def test_rejeitar_combinacao_inconsistente_no_fluxo_individual():
    evento = criar_evento_peca()
    evento["sensores"] = {"indutivo": True, "capacitivo": False}
    aprovado, erros = validar_evento(evento)
    assert aprovado is False
    assert any("inconsistente" in erro for erro in erros)


def test_validar_evento_sem_peca():
    aprovado, erros = validar_evento(criar_evento_sem_peca())
    assert aprovado is True
    assert erros == []


def test_rejeitar_sem_peca_com_sensor_ativo():
    evento = criar_evento_sem_peca()
    evento["sensores"]["capacitivo"] = True
    aprovado, erros = validar_evento(evento)
    assert aprovado is False
    assert any("SEM_PECA" in erro for erro in erros)


def test_rejeitar_timestamp_sem_fuso():
    evento = criar_evento_peca()
    evento["timestamp"] = "2026-11-11T18:00:00"
    aprovado, erros = validar_evento(evento)
    assert aprovado is False
    assert any("Timestamp" in erro for erro in erros)


def test_identificar_eventos_duplicados():
    primeiro = criar_evento_peca()
    segundo = criar_evento_peca()
    validos, invalidos = validar_eventos([primeiro, segundo])
    assert len(validos) == 1
    assert len(invalidos) == 1
    assert "Identificador duplicado." in invalidos[0]["erros"]


def test_separar_validos_e_invalidos():
    eventos = [criar_evento_peca(), criar_evento_sem_peca()]
    invalido = criar_evento_sem_peca()
    invalido["sensores"]["indutivo"] = True
    eventos.append(invalido)
    validos, invalidos = validar_eventos(eventos)
    assert len(validos) == 2
    assert len(invalidos) == 1


def test_rejeitar_tipo_antigo_de_nivel_reservatorio():
    evento = {
        "id": "NIVEL-001",
        "equipamento": "ESTEIRA-01",
        "timestamp": "2026-11-11T18:00:00Z",
        "tipoEvento": "NIVEL_RESERVATORIO",
        "reservatorioId": "METALICA",
        "nivel": 42.0,
    }
    aprovado, erros = validar_evento(evento)
    assert aprovado is False
    assert any("Tipo de evento desconhecido" in erro for erro in erros)


def test_rejeitar_entrada_que_nao_seja_lista():
    validos, invalidos = validar_eventos({})
    assert validos == []
    assert len(invalidos) == 1
