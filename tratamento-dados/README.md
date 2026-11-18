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

1. A API valida o cabeçalho do lote e cada evento.
2. O equipamento informado no lote é associado aos eventos.
3. Os eventos recebidos são preservados nos CSVs por data; erros e combinações inconsistentes são registrados separadamente.
4. Após a gravação, o pipeline relê o histórico CSV e executa classificação, indicadores gerais, consolidação por minuto, análise estatística dos reservatórios e detecção de anomalias.
5. Os resultados calculados são devolvidos na resposta da API. Nesta etapa, ainda não são enviados ao Spring Boot nem persistidos no MySQL.

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

## Integração manual com Spring Boot

Nesta etapa, a sincronização é executada manualmente para validar os contratos
com dados já armazenados nos CSVs. Ela não é disparada automaticamente a cada
lote recebido pela API de automação.

1. Inicie o MySQL e o backend Spring Boot.
2. Copie `.env.example` para `.env` nesta pasta e ajuste `SPRING_BOOT_BASE_URL`
   se necessário (padrão: `http://localhost:8080`).
3. Com o ambiente virtual ativo e estando na pasta `tratamento-dados`, execute:

   ```bash
   python scripts/sincronizar_com_springboot.py
   ```

O script recalcula o histórico CSV, consulta o histórico de produção do Spring
Boot para não reenviar intervalos já cadastrados e envia as anomalias uma a uma.
O backend responde HTTP 409 para anomalias já existentes, que são contabilizadas
como duplicadas. As contagens de produção são enviadas no contrato snake_case
esperado pelo DTO Java; o identificador de anomalia `id_origem` é convertido para
`id`, conforme o DTO atual do Spring Boot.

Esta sincronização manual é apropriada para os testes iniciais. Para operação
contínua, será necessário evoluir para uma fila/outbox persistente e uma regra
que só envie minutos encerrados, evitando publicar um minuto ainda em andamento.
