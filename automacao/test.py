
import json
import threading
import time
import uuid
from datetime import datetime, timezone

import requests


# ============================================================
# 1. CONFIGURAÇÕES
# ============================================================

URL_API = "http://10.110.12.21:8000/api/v1/automacao/leituras"
API = "http://10.110.12.37:5000"

EQUIPAMENTO = "ESTEIRA-01"

INTERVALO_ENVIO = 5

# Tempo sem detecção para encerrar uma peça
FIM_EVENTO = 0.3

# Valor que representa o indutivo livre
IND_LIVRE = 0x7FE0

# Reservatórios
CAPACIDADE_RESERVATORIO = 5

ALVO_METALICA_CM = 7
ALVO_NAO_METALICA_CM = 15

# Confirmação da chegada ao reservatório
CONFIRMA_DIST_S = 0.2

# Tempo para rearmar o sensor de distância
TEMPO_REARME_S = 0.2

# Relatório de erros
INTERVALO_RELATORIO_ERROS = 5


# ============================================================
# 2. SESSÃO HTTP
# ============================================================

session = requests.Session()


# ============================================================
# 3. FILAS E CONTROLES
# ============================================================

# Eventos de detecção da esteira
pendentes_esteira = []

# Eventos dos reservatórios
pendentes_reservatorio = []

trava = threading.Lock()

lote_seq = 0

# Peças classificadas que ainda aguardam chegar ao reservatório
pecas_aguardando_reservatorio = []

# Contadores dos reservatórios
contadores_reservatorio = {
    "METALICA": 0,
    "NAO_METALICA": 0
}


# ============================================================
# 4. CONTROLE DE ERROS
# ============================================================

erros_sensores = {
    "capacitivo/indutivo": {
        "quantidade": 0,
        "ultimo_erro": None
    },
    "distancia": {
        "quantidade": 0,
        "ultimo_erro": None
    }
}

ultimo_relatorio_erros = time.monotonic()


def registrar_erro(sensor, erro):

    erros_sensores[sensor]["quantidade"] += 1
    erros_sensores[sensor]["ultimo_erro"] = str(erro)


def relatar_erros():

    global ultimo_relatorio_erros

    agora_t = time.monotonic()

    if agora_t - ultimo_relatorio_erros < INTERVALO_RELATORIO_ERROS:
        return

    ultimo_relatorio_erros = agora_t

    for sensor, dados in erros_sensores.items():

        quantidade = dados["quantidade"]

        if quantidade > 0:

            print(
                f"\n[{agora()}] ERRO - Sensor {sensor}: "
                f"{quantidade} falhas nos últimos "
                f"{INTERVALO_RELATORIO_ERROS} segundos."
            )

            print(f"Último erro: {dados['ultimo_erro']}")

            dados["quantidade"] = 0
            dados["ultimo_erro"] = None


# ============================================================
# 5. FUNÇÕES AUXILIARES
# ============================================================

def agora():

    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def agora_utc():

    return datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def ler(nome):

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

    # Verifica se a API realmente retornou o campo data
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
            f"Valor inválido recebido do sensor {nome}: "
            f"{dados['value']}"
        )


# ============================================================
# 6. MONTAGEM DOS JSONs
# ============================================================

def montar_payload(leituras):

    global lote_seq

    lote_seq += 1

    enviado_em = agora_utc()

    return {
        "loteId": (
            f"LOTE-{enviado_em[:10].replace('-', '')}-"
            f"{lote_seq:03d}"
        ),
        "equipamento": EQUIPAMENTO,
        "enviadoEm": enviado_em,
        "intervaloSegundos": INTERVALO_ENVIO,
        "leituras": leituras
    }


# ============================================================
# 7. REGISTRO DOS EVENTOS DA ESTEIRA
# ============================================================

def adicionar_evento_peca(tipo, ts, indutivo, capacitivo):

    leitura = {
        "id": str(uuid.uuid4()),
        "timestamp": ts,
        "tipoEvento": tipo,
        "sensores": {
            "indutivo": indutivo,
            "capacitivo": capacitivo
        }
    }

    with trava:
        pendentes_esteira.append(leitura)


# ============================================================
# 8. REGISTRO DOS EVENTOS DOS RESERVATÓRIOS
# ============================================================

def registrar_queda_reservatorio(reservatorio_id):

    contadores_reservatorio[reservatorio_id] += 1

    qtd = contadores_reservatorio[reservatorio_id]

    nivel = round(
        (qtd / CAPACIDADE_RESERVATORIO) * 100,
        2
    )

    evento = {
        "id": str(uuid.uuid4()),
        "timestamp": agora_utc(),
        "tipoEvento": "NIVEL_RESERVATORIO",
        "reservatorioId": reservatorio_id,
        "nivel": nivel
    }

    with trava:
        pendentes_reservatorio.append(evento)

    # Reset lógico ao atingir a capacidade
    if qtd >= CAPACIDADE_RESERVATORIO:

        contadores_reservatorio[reservatorio_id] = 0


# ============================================================
# 9. ENVIO DOS POSTs
# ============================================================

def devolver_para_fila(fila, leituras):

    with trava:
        fila[:0] = leituras


def enviar_post(payload, fila):

    print("\n========== JSON ENVIADO ==========")

    print(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False
        )
    )

    print("==================================")

    try:

        resposta = requests.post(
            URL_API,
            json=payload,
            timeout=3
        )

        # Erro de validação: não reenviar automaticamente
        if resposta.status_code == 422:

            print(
                f"[{agora()}] ERRO HTTP 422 - "
                "O backend rejeitou o JSON."
            )

            print(resposta.text)

            return

        # Erros internos do servidor
        if resposta.status_code >= 500:

            print(
                f"[{agora()}] ERRO HTTP "
                f"{resposta.status_code}. "
                "Eventos devolvidos para a fila."
            )

            devolver_para_fila(
                fila,
                payload["leituras"]
            )

            return

        # Outros erros de requisição
        if resposta.status_code >= 400:

            print(
                f"[{agora()}] ERRO HTTP "
                f"{resposta.status_code}: {resposta.text}"
            )

            return

        print(
            f"[{agora()}] POST enviado com sucesso: "
            f"{payload['loteId']} | "
            f"HTTP {resposta.status_code} | "
            f"{len(payload['leituras'])} eventos"
        )

    except requests.exceptions.RequestException as e:

        print(
            f"[{agora()}] ERRO DE COMUNICAÇÃO NO POST: {e}"
        )

        devolver_para_fila(
            fila,
            payload["leituras"]
        )


def enviar_lotes():

    with trava:

        lote_esteira = pendentes_esteira.copy()
        lote_reservatorio = pendentes_reservatorio.copy()

        pendentes_esteira.clear()
        pendentes_reservatorio.clear()

    # --------------------------------------------------------
    # POST 1 - EVENTOS DA ESTEIRA
    # --------------------------------------------------------

    if lote_esteira:

        payload_esteira = montar_payload(lote_esteira)

        threading.Thread(
            target=enviar_post,
            args=(
                payload_esteira,
                pendentes_esteira
            ),
            daemon=True
        ).start()

    # --------------------------------------------------------
    # POST 2 - EVENTOS DOS RESERVATÓRIOS
    # --------------------------------------------------------

    if lote_reservatorio:

        payload_reservatorio = montar_payload(
            lote_reservatorio
        )

        threading.Thread(
            target=enviar_post,
            args=(
                payload_reservatorio,
                pendentes_reservatorio
            ),
            daemon=True
        ).start()


# ============================================================
# 10. ESTADOS DA DETECÇÃO DAS PEÇAS
# ============================================================

em_evento = False

cap_visto = False
ind_visto = False

ts_evento = ""

ultimo_detectado = 0.0


# ============================================================
# 11. ESTADOS DO SENSOR DE DISTÂNCIA
# ============================================================

distancia_armada = True

alvo_em_confirmacao = None
inicio_confirmacao = 0.0

inicio_rearme = None


# ============================================================
# 12. CONTROLE DO ENVIO
# ============================================================

ultimo_envio = time.monotonic()


# ============================================================
# 13. LOOP PRINCIPAL
# ============================================================

while True:

    # --------------------------------------------------------
    # A. RELATÓRIO DE ERROS A CADA 5 SEGUNDOS
    # --------------------------------------------------------

    relatar_erros()

    agora_t = time.monotonic()

    # --------------------------------------------------------
    # B. ENVIO DOS DOIS LOTES A CADA 5 SEGUNDOS
    # --------------------------------------------------------

    if agora_t - ultimo_envio >= INTERVALO_ENVIO:

        ultimo_envio = agora_t

        enviar_lotes()

    # --------------------------------------------------------
    # C. LEITURA DO CAPACITIVO E INDUTIVO
    # --------------------------------------------------------

    try:

        cap = ler("capacitivo")
        ind = ler("indutivo")

    except Exception as e:

        registrar_erro(
            "capacitivo/indutivo",
            e
        )

        time.sleep(0.02)
        continue

    capacitivo = (cap & 1) == 1

    indutivo = ind != IND_LIVRE

    # --------------------------------------------------------
    # D. DETECÇÃO E CLASSIFICAÇÃO DA PEÇA
    # --------------------------------------------------------

    agora_t = time.monotonic()

    detectando = capacitivo or indutivo

    if detectando:

        # Começo de um novo evento
        if not em_evento:

            em_evento = True

            ts_evento = agora_utc()

            cap_visto = False
            ind_visto = False

        ultimo_detectado = agora_t

        # Guarda todas as ativações observadas
        # durante a passagem da peça
        cap_visto = cap_visto or capacitivo

        ind_visto = ind_visto or indutivo

    # --------------------------------------------------------
    # E. ENCERRAMENTO E CLASSIFICAÇÃO
    # --------------------------------------------------------

    if (
        em_evento
        and not detectando
        and agora_t - ultimo_detectado >= FIM_EVENTO
    ):

        # Se o indutivo ativou em qualquer momento,
        # a peça é considerada metálica.
        if ind_visto:

            classificacao = "METALICA"

        else:

            classificacao = "NAO_METALICA"

        # Registra a peça detectada
        adicionar_evento_peca(
            "PECA_DETECTADA",
            ts_evento,
            ind_visto,
            cap_visto
        )

        # Adiciona a classificação à fila
        pecas_aguardando_reservatorio.append(
            classificacao
        )

        # Registra o fim da detecção
        adicionar_evento_peca(
            "SEM_PECA",
            agora_utc(),
            False,
            False
        )

        # Finaliza o evento
        em_evento = False

        cap_visto = False
        ind_visto = False

    # --------------------------------------------------------
    # F. LEITURA INDEPENDENTE DO SENSOR DE DISTÂNCIA
    # --------------------------------------------------------

    dist_cm = None

    try:

        dist_raw = ler("distancia")

        # Conversão calibrada:
        # hexadecimal -> decimal -> divisão inteira por 16
        dist_cm = dist_raw // 16

    except Exception as e:

        registrar_erro(
            "distancia",
            e
        )

    # --------------------------------------------------------
    # G. IDENTIFICAÇÃO DA CHEGADA AO RESERVATÓRIO
    # --------------------------------------------------------

    # Só executa se a leitura de distância foi válida
    if (
        dist_cm is not None
        and pecas_aguardando_reservatorio
    ):

        proximo_destino = pecas_aguardando_reservatorio[0]

        if proximo_destino == "METALICA":

            alvo_esperado = ALVO_METALICA_CM

        else:

            alvo_esperado = ALVO_NAO_METALICA_CM

        # ----------------------------------------------------
        # SENSOR ARMADO: verifica chegada da peça
        # ----------------------------------------------------

        if distancia_armada:

            if dist_cm == alvo_esperado:

                if alvo_em_confirmacao != alvo_esperado:

                    alvo_em_confirmacao = alvo_esperado

                    inicio_confirmacao = time.monotonic()

                elif (
                    time.monotonic() - inicio_confirmacao
                    >= CONFIRMA_DIST_S
                ):

                    # Confirma a chegada ao reservatório
                    registrar_queda_reservatorio(
                        proximo_destino
                    )

                    # Remove a peça já contabilizada
                    pecas_aguardando_reservatorio.pop(0)

                    # Desarma para evitar contagem duplicada
                    distancia_armada = False

                    alvo_em_confirmacao = None
                    inicio_rearme = None

            else:

                alvo_em_confirmacao = None

                # Se atingiu o alvo do outro reservatório,
                # não contabiliza e mantém a peça na fila.
                if dist_cm in (
                    ALVO_METALICA_CM,
                    ALVO_NAO_METALICA_CM
                ):

                    pass

        # ----------------------------------------------------
        # SENSOR DESARMADO: espera sair da faixa de chegada
        # ----------------------------------------------------

        else:

            if dist_cm not in (
                ALVO_METALICA_CM,
                ALVO_NAO_METALICA_CM
            ):

                if inicio_rearme is None:

                    inicio_rearme = time.monotonic()

                elif (
                    time.monotonic() - inicio_rearme
                    >= TEMPO_REARME_S
                ):

                    distancia_armada = True

                    inicio_rearme = None

            else:

                inicio_rearme = None

    # --------------------------------------------------------
    # H. PEQUENA PAUSA DO LOOP
    # --------------------------------------------------------

    time.sleep(0.01)
