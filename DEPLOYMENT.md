# Deployment Guide

Guia inicial para preparar o projeto em uma VPS.

O alvo atual do projeto e:

- PostgreSQL OLTP hospitalar.
- Simulador Python para seed e stream.
- CDC local/opcional com Debezium e Kafka.
- Dashboard operacional em streaming.

S3, Databricks, raw lake e consumers de lake foram removidos do escopo.

## Fluxo Recomendado

1. Validar tudo localmente.
2. Criar o dashboard operacional local.
3. Preparar variaveis e portas para VPS.
4. Subir Postgres, simulador, CDC e dashboard de forma controlada.
5. Configurar dominio, HTTPS, logs e backup do PostgreSQL.

## Comandos Base

```bash
make up
make test-connection
make test
make test-integration
make cdc-up
make connector-status
```

## Pendente

- Definir layout final dos servicos na VPS.
- Criar service files ou Compose de producao.
- Definir backup local/remoto do PostgreSQL.
- Definir autenticacao para o dashboard.
- Definir portas publicas e reverse proxy.
