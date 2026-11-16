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
