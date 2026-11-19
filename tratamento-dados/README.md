## API e processamento de dados

Instale as dependências a partir desta pasta:

```bash
python -m pip install -r requirements.txt
```

Inicie o servidor:

```bash
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

- Documentação interativa: `http://localhost:8000/docs`
- Health check: `GET http://localhost:8000/health`
- Recepção: `POST http://localhost:8000/api/v1/automacao/leituras`

### Fluxo atual

1. A API valida o cabeçalho do lote e cada evento recebido.
2. O equipamento informado no lote é associado aos eventos.
3. Os eventos brutos são preservados em CSV por data; eventos inconsistentes são mantidos e registrados separadamente.
4. O pipeline relê o histórico CSV e executa classificação, consolidação por minuto, estatísticas dos reservatórios e detecção de anomalias.
5. A cada lote recebido, os períodos já encerrados e as anomalias são sincronizados com o Spring Boot. Se o backend estiver indisponível, os dados permanecem preservados em CSV para nova tentativa quando chegar outro lote.
6. O React consulta o Spring Boot para indicadores operacionais e esta API Python para as estatísticas descritivas dos reservatórios. O React não recebe dados brutos dos sensores.

### Contrato JSON — Automação para Tratamento de Dados

Endpoint: `POST /api/v1/automacao/leituras`

O lote deve seguir esta estrutura:

```json
{
  "loteId": "LOTE-20261118-001",
  "equipamento": "ESTEIRA-01",
  "enviadoEm": "2026-11-18T20:00:00Z",
  "intervaloSegundos": 5,
  "leituras": [
    {
      "id": "EVENTO-001",
      "timestamp": "2026-11-18T20:00:00Z",
      "tipoEvento": "PECA_DETECTADA",
      "sensores": {
        "indutivo": true,
        "capacitivo": true
      }
    },
    {
      "id": "EVENTO-002",
      "timestamp": "2026-11-18T20:00:05Z",
      "tipoEvento": "NIVEL_RESERVATORIO",
      "reservatorioId": "METALICA",
      "nivel": 82.5
    }
  ]
}
```

Cada leitura deve ter identificador único (`id`) e timestamp com fuso horário. `tipoEvento` aceita `PECA_DETECTADA` ou `NIVEL_RESERVATORIO`. Para níveis, `reservatorioId` aceita `METALICA` ou `NAO_METALICA`, e `nivel` é numérico, não negativo e não representa percentual por convenção.

### Contrato Tratamento de Dados para Spring Boot

A produção é enviada por minuto encerrado para `POST /api/v1/analytics/production`:

```json
{
  "inicio_intervalo": "2026-11-18T20:00:00Z",
  "total_pecas": 35,
  "pecas_metalicas": 20,
  "pecas_nao_metalicas": 15
}
```

As anomalias são enviadas para `POST /api/v1/analytics/anomalies`, no DTO definido pelo backend Java. Estatísticas descritivas permanecem calculadas em Python e não são persistidas no MySQL.

### Regras de classificação

- `indutivo=true` e `capacitivo=true`: `METALICA`.
- `indutivo=false` e `capacitivo=true`: `NAO_METALICA`.
- Ambos `false`: `SEM_PECA` (não contabiliza produção).
- `indutivo=true` e `capacitivo=false`: `INCONSISTENTE` (preserva e contabiliza separadamente, sem somar como peça).

### Testes

Execute a suíte a partir desta pasta:

```bash
python -m pytest -q
```

## Configuração da Automação

O módulo `automacao/automacao-test` envia lotes a cada 5 segundos. Os endereços de rede padrão permanecem preservados em `config.py` e podem ser sobrescritos por variáveis de ambiente:

- `METALTECH_DATA_API`: URL completa do endpoint FastAPI.
- `METALTECH_SENSOR_API`: endereço-base do serviço/gateway de sensores.

Para teste local, configure `METALTECH_DATA_API` como `http://localhost:8000/api/v1/automacao/leituras`. A leitura física depende de acesso ao gateway configurado em `METALTECH_SENSOR_API`; sem sensores disponíveis, use os lotes de exemplo ou o Swagger para validar o processamento.

## Testes

Execute a suíte a partir desta pasta:

```bash
python -m pytest -q
```
