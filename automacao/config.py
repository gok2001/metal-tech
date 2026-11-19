# ============================================================
# CONFIGURAÇÕES GERAIS
# ============================================================

URL_API = "http://10.110.12.21:8000/api/v1/automacao/leituras"
API = "http://10.110.12.37:5000"

EQUIPAMENTO = "ESTEIRA-01"
INTERVALO_ENVIO = 5
INTERVALO_LOOP = 0.02

# Detecção e classificação
FIM_EVENTO = 0.3
IND_LIVRE = 0x7FE0

# Reservatórios
CAPACIDADE_RESERVATORIO = 5
ALVO_METALICA_CM = 7
ALVO_NAO_METALICA_CM = 15
TOLERANCIA_DIST = 1
CONFIRMA_DIST_S = 0.1
TEMPO_REARME_S = 0.2

# Relatório de erros
INTERVALO_RELATORIO_ERROS = 5