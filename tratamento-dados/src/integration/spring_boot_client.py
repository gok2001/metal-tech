"""Cliente HTTP para enviar dados processados ao Spring Boot."""

from datetime import datetime, timezone
import os

import requests
from dotenv import load_dotenv


class SpringBootIntegrationError(RuntimeError):
    """Falha ao comunicar com a API Spring Boot."""


class SpringBootClient:
    def __init__(self, base_url=None, timeout=None, session=None):
        load_dotenv()
        self.base_url = (base_url or os.getenv(
            "SPRING_BOOT_BASE_URL", "http://localhost:8080"
        )).rstrip("/")
        self.timeout = timeout or float(os.getenv("SPRING_BOOT_TIMEOUT", "10"))
        self.session = session or requests.Session()

    def _request(self, method, path, **kwargs):
        try:
            response = self.session.request(
                method,
                f"{self.base_url}{path}",
                timeout=self.timeout,
                **kwargs,
            )
        except requests.RequestException as exc:
            raise SpringBootIntegrationError(
                f"Não foi possível conectar ao Spring Boot em {self.base_url}: {exc}"
            ) from exc

        if not response.ok:
            raise SpringBootIntegrationError(
                f"Spring Boot respondeu HTTP {response.status_code} em {path}: "
                f"{response.text[:500]}"
            )
        return response

    @staticmethod
    def _normalizar_periodo(valor):
        data = datetime.fromisoformat(valor.replace("Z", "+00:00"))
        if data.tzinfo is None:
            data = data.replace(tzinfo=timezone.utc)
        return data.astimezone(timezone.utc).replace(tzinfo=None).isoformat(timespec="seconds")

    def periodos_ja_registrados(self):
        response = self._request("GET", "/api/v1/analytics/production")
        try:
            historico = response.json()
            return {
                self._normalizar_periodo(item["inicioIntervalo"])
                for item in historico
                if item.get("inicioIntervalo")
            }
        except (ValueError, TypeError, KeyError) as exc:
            raise SpringBootIntegrationError(
                "Resposta inválida ao consultar o histórico de produção do Spring Boot."
            ) from exc

    def enviar_producao(self, registro):
        payload = {
            "inicio_intervalo": registro["periodo"],
            "total_pecas": registro["total"],
            "pecas_metalicas": registro["metalicas"],
            "pecas_nao_metalicas": registro["naoMetalicas"],
        }
        return self._request(
            "POST", "/api/v1/analytics/production", json=payload
        )

    def enviar_anomalia(self, anomalia):
        # O DTO Java chama o identificador de origem de "id".
        payload = {
            "id": anomalia["id_origem"],
            "tipo": anomalia["tipo"],
            "equipamento": anomalia["equipamento"],
            "tipo_reservatorio": anomalia.get("tipo_reservatorio"),
            "descricao": anomalia["descricao"],
            "severidade": anomalia["severidade"],
            "data_ocorrencia": anomalia["data_ocorrencia"],
        }
        return self._request(
            "POST", "/api/v1/analytics/anomalies", json=payload
        )

    def sincronizar(self, processamento):
        """Envia contagens ainda ausentes e anomalias do processamento fornecido.

        A sincronização é deliberadamente manual nesta etapa. A produção é
        deduplicada consultando o histórico Java; anomalias repetidas recebem
        HTTP 409 do backend e são contabilizadas como já existentes.
        """
        periodos_existentes = self.periodos_ja_registrados()
        resultado = {
            "producoes_enviadas": 0,
            "producoes_ja_existentes": 0,
            "anomalias_enviadas": 0,
            "anomalias_ja_existentes": 0,
        }

        for registro in processamento.get("producaoPorMinuto", []):
            periodo = self._normalizar_periodo(registro["periodo"])
            if periodo in periodos_existentes:
                resultado["producoes_ja_existentes"] += 1
                continue
            self.enviar_producao(registro)
            periodos_existentes.add(periodo)
            resultado["producoes_enviadas"] += 1

        for anomalia in processamento.get("anomalias", []):
            try:
                self.enviar_anomalia(anomalia)
                resultado["anomalias_enviadas"] += 1
            except SpringBootIntegrationError as exc:
                if "HTTP 409" in str(exc):
                    resultado["anomalias_ja_existentes"] += 1
                    continue
                raise

        return resultado
