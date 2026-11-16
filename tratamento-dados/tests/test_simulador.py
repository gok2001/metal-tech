
import json

from pathlib import Path
from src.processing.validator import validar_eventos


def test_validar_dados_do_simulador():

    caminho = Path("data/samples/leituras_exemplo.json")

    with open(caminho, "r", encoding="utf-8") as arquivo:
        eventos = json.load(arquivo)

    validos, invalidos = validar_eventos(eventos)

    print(f"\nTotal de eventos: {len(eventos)}")
    print(f"Eventos válidos: {len(validos)}")
    print(f"Eventos inválidos: {len(invalidos)}")

    assert len(eventos) > 0
    assert len(validos) + len(invalidos) == len(eventos)
