# Project Context

## Objetivo

Simular um banco OLTP hospitalar em PostgreSQL para gerar eventos realistas de INSERT/UPDATE, testar CDC e alimentar um dashboard operacional em streaming.

## Stack Atual

- Python 3.11 no Docker.
- Python local pode variar; a venv antiga estava em 3.9, mas o projeto declara 3.11+.
- PostgreSQL via `debezium/postgres:16`.
- CLI com Typer.
- Dashboard Streamlit.
- Dados fake com Faker `pt_BR`.
- Docker Compose com perfis:
  - default: `postgres`
  - `simulator`: app Python containerizada
  - `cdc`: Kafka, Kafka Connect, Kafka UI

## Configuracao

Fonte oficial da aplicacao:

```text
config/.env
```

O `.env` da raiz pode existir para outros usos, mas nao deve ser usado como configuracao do simulador.

## Estado Validado

Validado localmente:

- `make test`
- `make test-connection`
- `make reset`
- `make stream-test`
- `make docker-build`
- `make docker-test`
- `make docker-stream-test`
- `make cdc-up`
- `make connector-status`
- `make dashboard-test`

## Pontos de Atencao

- `config/.env` e ignorado pelo Git.
- O Compose default deve continuar subindo somente Postgres.
- S3, Databricks, raw lake e consumer de lake foram removidos do escopo.
- Dashboard operacional local existe em `app/dashboard.py` e le PostgreSQL direto.
- Proximo passo do dashboard: empacotar em Docker e preparar VPS.
