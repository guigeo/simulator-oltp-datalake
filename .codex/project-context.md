# Project Context

## Objetivo

Simular um banco OLTP hospitalar em PostgreSQL para gerar eventos realistas de INSERT/UPDATE e testar pipelines CDC.

## Stack Atual

- Python 3.11 no Docker.
- Python local pode variar; a venv antiga estava em 3.9, mas o projeto declara 3.11+.
- PostgreSQL via `debezium/postgres:16`.
- CLI com Typer.
- Dados fake com Faker `pt_BR`.
- Docker Compose com perfis:
  - default: `postgres`
  - `simulator`: app Python containerizada
  - `cdc`: Kafka, Kafka Connect, Kafka UI
  - `lake`: CDC + consumer raw

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

## Pontos de Atencao

- `config/.env` e ignorado pelo Git.
- O Compose default deve continuar subindo somente Postgres.
- O profile `lake` ainda nao foi validado como pipeline completo.
- `consumer_universal.py` ainda precisa refatoracao antes de uso serio.
- Databricks Bronze SQL ainda precisa revisao de contrato com o formato raw.

