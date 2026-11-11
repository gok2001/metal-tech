
import csv
import json

from datetime import datetime, timezone
from pathlib import Path


class CSVManager:
    """Gerencia o armazenamento histórico das leituras industriais."""

    CAMPOS_LEITURAS = [
        "received_at",
        "event_id",
        "equipamento",
        "event_timestamp",
        "tipo_evento",
        "payload_json"
    ]

    CAMPOS_ERROS = [
        "received_at",
        "event_id",
        "erros"
    ]

    def __init__(self, diretorio_base=None):

        if diretorio_base is None:
            raiz_projeto = Path(__file__).resolve().parents[2]
            diretorio_base = raiz_projeto / "data" / "raw"

        self.diretorio_base = Path(diretorio_base)

    def _obter_data_evento(self, evento, recebido_em):
        """Utiliza o timestamp do evento ou a data de recebimento."""

        if isinstance(evento, dict):
            timestamp = evento.get("timestamp")

            if isinstance(timestamp, str):
                try:
                    data = datetime.fromisoformat(
                        timestamp.replace("Z", "+00:00")
                    )
                    return data.date()
                except ValueError:
                    pass

        return recebido_em.date()

    def _obter_caminhos(self, data):
        """Monta os caminhos dos arquivos organizados por data."""

        pasta = (
            self.diretorio_base
            / str(data.year)
            / f"{data.month:02d}"
            / f"{data.day:02d}"
        )

        pasta.mkdir(parents=True, exist_ok=True)

        return (
            pasta / "leituras.csv",
            pasta / "erros.csv"
        )

    def _id_ja_registrado(self, caminho, identificador):
        """Verifica se o identificador já consta no histórico."""

        if not identificador or not caminho.exists():
            return False

        with open(caminho, "r", newline="", encoding="utf-8") as arquivo:
            leitor = csv.DictReader(arquivo)

            return any(
                linha.get("event_id") == identificador
                for linha in leitor
            )

    def salvar_evento(self, evento, erros=None):
        """
        Salva uma mensagem no histórico bruto.

        Mensagens inválidas também são preservadas e registradas
        no arquivo de erros.

        Retorna False quando o evento já foi registrado.
        """

        recebido_em = datetime.now(timezone.utc)

        data_evento = self._obter_data_evento(
            evento,
            recebido_em
        )

        caminho_leituras, caminho_erros = self._obter_caminhos(
            data_evento
        )

        if isinstance(evento, dict):
            identificador = evento.get("id", "")
            equipamento = evento.get("equipamento", "")
            timestamp = evento.get("timestamp", "")
            tipo_evento = evento.get("tipoEvento", "")
        else:
            identificador = ""
            equipamento = ""
            timestamp = ""
            tipo_evento = ""

        if self._id_ja_registrado(
            caminho_leituras,
            identificador
        ):
            return False

        registro = {
            "received_at": recebido_em.isoformat(),
            "event_id": identificador,
            "equipamento": equipamento,
            "event_timestamp": timestamp,
            "tipo_evento": tipo_evento,
            "payload_json": json.dumps(
                evento,
                ensure_ascii=False
            )
        }

        arquivo_novo = not caminho_leituras.exists()

        with open(
            caminho_leituras,
            "a",
            newline="",
            encoding="utf-8"
        ) as arquivo:

            escritor = csv.DictWriter(
                arquivo,
                fieldnames=self.CAMPOS_LEITURAS
            )

            if arquivo_novo:
                escritor.writeheader()

            escritor.writerow(registro)

        if erros:

            registro_erro = {
                "received_at": recebido_em.isoformat(),
                "event_id": identificador,
                "erros": " | ".join(erros)
            }

            arquivo_novo = not caminho_erros.exists()

            with open(
                caminho_erros,
                "a",
                newline="",
                encoding="utf-8"
            ) as arquivo:

                escritor = csv.DictWriter(
                    arquivo,
                    fieldnames=self.CAMPOS_ERROS
                )

                if arquivo_novo:
                    escritor.writeheader()

                escritor.writerow(registro_erro)

        return True
