import requests

from automacao.automacao_test.config import API

session = requests.Session()


def ler(nome):
    """Lê um sensor no gateway e retorna seu valor hexadecimal como inteiro."""

    url = f"{API}/sensores/{nome}"
    resposta = session.get(url, timeout=0.5)
    resposta.raise_for_status()

    try:
        conteudo = resposta.json()
    except ValueError:
        raise ValueError(
            f"Resposta do sensor {nome} não contém JSON válido: "
            f"{resposta.text[:300]}"
        )

    if not isinstance(conteudo, dict) or "data" not in conteudo:
        raise ValueError(
            f"Resposta inesperada do sensor {nome}: {conteudo}"
        )

    dados = conteudo["data"]

    if not isinstance(dados, dict) or "value" not in dados:
        raise ValueError(
            f"Campo data.value ausente no sensor {nome}: {conteudo}"
        )

    try:
        return int(dados["value"], 16)
    except (ValueError, TypeError):
        raise ValueError(
            f"Valor inválido recebido do sensor {nome}: {dados['value']}"
        )
