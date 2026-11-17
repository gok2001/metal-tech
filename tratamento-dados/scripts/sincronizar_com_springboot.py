"""Executa uma sincronização manual do histórico CSV com o Spring Boot.

Execute na pasta tratamento-dados:
    python scripts/sincronizar_com_springboot.py
"""

from src.integration.spring_boot_client import (
    SpringBootClient,
    SpringBootIntegrationError,
)
from src.processing.pipeline import processar_historico
from src.storage.csv_manager import CSVManager


def main():
    eventos = CSVManager().listar_eventos()
    processamento = processar_historico(eventos)

    if not eventos:
        print("Nenhum evento foi encontrado nos CSVs para sincronização.")
        return

    cliente = SpringBootClient()
    try:
        resultado = cliente.sincronizar(processamento)
    except SpringBootIntegrationError as exc:
        print(f"Falha na sincronização: {exc}")
        raise SystemExit(1) from exc

    print("Sincronização concluída:")
    for indicador, quantidade in resultado.items():
        print(f"- {indicador}: {quantidade}")


if __name__ == "__main__":
    main()
