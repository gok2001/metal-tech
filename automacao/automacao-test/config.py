# ============================================================
# CONFIGURAÇÕES GERAIS
# ============================================================
# Os endereços padrão preservam a configuração atual da rede industrial.
# Para testes locais, podem ser sobrescritos sem editar este arquivo:
#   METALTECH_DATA_API=http://localhost:8000/api/v1/automacao/leituras
#   METALTECH_SENSOR_API=http://10.110.12.37:5000

import os

URL_API = os.getenv(
    "METALTECH_DATA_API",
    "http://10.110.12.21:8000/api/v1/automacao/leituras"
)
API = os.getenv("METALTECH_SENSOR_API", "http://10.110.12.37:5000")

EQUIPAMENTO = "ESTEIRA-01"
INTERVALO_ENVIO = 5
INTERVALO_LOOP = 0.01

# Detecção e classificação
FIM_EVENTO = 0.3
IND_LIVRE = 0x7FE0

# Reservatórios
CAPACIDADE_RESERVATORIO = 5
ALVO_METALICA_CM = 7
ALVO_NAO_METALICA_CM = 15
CONFIRMA_DIST_S = 0.2
TEMPO_REARME_S = 0.2

# Relatório de erros
INTERVALO_RELATORIO_ERROS = 5
