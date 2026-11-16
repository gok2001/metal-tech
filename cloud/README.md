# Docker# Execução local com Docker Compose

Este ambiente inicia o MySQL e a API de monitoramento em containers.

## Requisitos

- Docker Engine
- Docker Compose v2

## Configuração

Na raiz do repositório, crie o arquivo local de variáveis:

```bash
cp .env.example .env
```
Edite .env e substitua os valores de exemplo das senhas:

```bash
nano .env
```

O arquivo .env contém configurações locais e não deve ser commitado. 

Use .env.example como modelo.

## Iniciar os serviços

Execute os comandos a partir da raiz do repositório:

```bash
docker compose --env-file .env -f cloud/docker/docker-compose.yml config --quiet
docker compose --env-file .env -f cloud/docker/docker-compose.yml up --build -d
```

O Compose constrói a imagem da API, inicia o MySQL e aguarda o banco ficar saudável antes de iniciar o backend.

## Verificar

Confira o estado dos containers:

```bash
docker compose --env-file .env -f cloud/docker/docker-compose.yml ps
```

Consulte o histórico de produção:

```bash
curl -i http://localhost:8080/api/v1/analytics/production
```

Consulte os reservatórios:

```bash
curl -i http://localhost:8080/api/v1/analytics/reservoirs
```

A API fica disponível na porta 8080. O MySQL fica disponível na porta 3307 da máquina e na porta 3306 dentro da rede Docker.

## Parar os serviços

```bash
docker compose --env-file .env -f cloud/docker/docker-compose.yml down
```

Os dados do MySQL ficam em um volume Docker nomeado e permanecem guardados quando os containers são parados.