# AGENTS.md

Instrucoes para agentes trabalhando neste repositorio.

## Contexto do Projeto

Este projeto e um simulador OLTP hospitalar em Python/PostgreSQL para testes de CDC com Debezium, Kafka e uma futura camada raw/lake.

O trabalho atual segue uma estrategia local-first:

1. manter Postgres + simulador funcionando localmente;
2. testar e refatorar em passos pequenos;
3. so depois ativar CDC/Kafka;
4. por ultimo preparar VPS.

## Regras de Trabalho

- Use `config/.env` como arquivo oficial de configuracao da aplicacao.
- Nao use o `.env` da raiz para configuracao do simulador.
- Preserve o fluxo local antes de mexer em CDC/S3/Databricks.
- Prefira mudancas pequenas e verificaveis.
- Nao rode comandos destrutivos como `make reset` sem autorizacao explicita do usuario.
- Antes de finalizar alteracoes, rode pelo menos:

```bash
make test
git diff --check
```

Quando mexer em Docker, tambem rode:

```bash
docker compose --profile simulator config --services
make docker-build
make docker-test
make docker-stream-test
```

## Comandos Principais

```bash
make up                # sobe Postgres local
make test-connection   # testa conexao
make reset             # recria e popula banco local
make counts            # contagens por tabela
make stream-test       # 5 ciclos de stream no host
make test              # testes unitarios
make docker-build      # build da imagem do simulador
make docker-test       # testes dentro do container
make docker-stream-test # 5 ciclos dentro do container
```

## Estado Atual

Commits recentes relevantes:

- `3d2ba83 Refactor local simulator workflow`
- `71ea34a Add Docker simulator workflow`
- `3775a68 Fix document generation and pin CLI dependency`

O branch `main` esta adiantado em relacao a `origin/main` por esses commits locais.

## Proximas Fases Sugeridas

1. Melhorar `seed.py`/`stream.py` com menos duplicacao e logs mais ricos.
2. Criar testes de integracao opcionais para Postgres.
3. Validar Compose `cdc` com Debezium/Kafka.
4. Refatorar `consumer_universal` antes de ativar S3/lake.
5. Preparar `VPS_RUNBOOK.md`.

