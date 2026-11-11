
import pytest

from src.processing.validator import (
    validar_evento,
    validar_eventos
)


def criar_evento_peca():
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


def criar_evento_reservatorio():
    return {
        "id": "LEITURA-002",
        "equipamento": "ESTEIRA-01",
        "timestamp": "2026-11-11T18:00:05Z",
        "tipoEvento": "NIVEL_RESERVATORIO",
        "nivelReservatorio": 65.0
    }


def test_validar_peca_metalica():
    evento = criar_evento_peca()

    aprovado, erros = validar_evento(evento)

    assert aprovado is True
    assert erros == []


def test_validar_peca_nao_metalica():
    evento = criar_evento_peca()
    evento["sensores"]["indutivo"] = False

    aprovado, erros = validar_evento(evento)

    assert aprovado is True
    assert erros == []


def test_rejeitar_combinacao_inconsistente():
    evento = criar_evento_peca()
    evento["sensores"]["indutivo"] = True
    evento["sensores"]["capacitivo"] = False

    aprovado, erros = validar_evento(evento)

    assert aprovado is False
    assert any("inconsistente" in erro for erro in erros)


def test_validar_nivel_reservatorio():
    evento = criar_evento_reservatorio()

    aprovado, erros = validar_evento(evento)

    assert aprovado is True
    assert erros == []


@pytest.mark.parametrize("nivel", [-1, 101, float("nan"), float("inf")])
def test_rejeitar_nivel_invalido(nivel):
    evento = criar_evento_reservatorio()
    evento["nivelReservatorio"] = nivel

    aprovado, erros = validar_evento(evento)

    assert aprovado is False
    assert len(erros) > 0


def test_rejeitar_timestamp_sem_fuso():
    evento = criar_evento_peca()
    evento["timestamp"] = "2026-11-11T18:00:00"

    aprovado, erros = validar_evento(evento)

    assert aprovado is False
    assert any("Timestamp" in erro for erro in erros)


def test_identificar_eventos_duplicados():
    primeiro = criar_evento_peca()
    segundo = criar_evento_peca()

    validos, invalidos = validar_eventos(
        [primeiro, segundo]
    )

    assert len(validos) == 1
    assert len(invalidos) == 1
    assert "Identificador duplicado." in invalidos[0]["erros"]


def test_separar_validos_e_invalidos():
    eventos = [
        criar_evento_peca(),
        criar_evento_reservatorio()
    ]

    evento_invalido = criar_evento_reservatorio()
    evento_invalido["nivelReservatorio"] = 150

    eventos.append(evento_invalido)

    validos, invalidos = validar_eventos(eventos)

    assert len(validos) == 2
    assert len(invalidos) == 1


def test_rejeitar_entrada_que_nao_seja_lista():
    validos, invalidos = validar_eventos({})

    assert validos == []
    assert len(invalidos) == 1
