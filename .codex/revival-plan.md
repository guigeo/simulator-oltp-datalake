# Revival Plan

## Fase 0: Diagnostico

Status: concluida.

- Docker local validado.
- Postgres local validado.
- `make reset`, `make counts`, `make stream-test` validados.

## Fase 1: Configuracao

Status: concluida.

- `config/.env` padronizado como fonte oficial.
- Compose default reduzido para Postgres.
- Perfis `cdc` e `simulator` separados.

## Fase 2: CLI e Makefile

Status: concluida.

- `stream --cycles`.
- `make stream-test`.
- `make test-connection`.
- `make init` idempotente.

## Fase 3: Nucleo do Simulador

Status: parcialmente concluida.

Concluido:

- `pacientes_convenios` agora conta insercoes reais.
- `update_internacao` respeita `data_entrada`.
- CNPJ/CPF normalizam digito verificador.

Pendente:

- Reduzir duplicacao em `seed.py`.
- Melhorar logs com ids afetados.
- Separar operacoes de stream em estrutura mais testavel.

## Fase 4: Testes

Status: iniciada.

Concluido:

- Testes unitarios com `unittest`.
- `make test`.
- Testes de geracao de dados, config e stream bounded.

Pendente:

- Testes de integracao Postgres opcionais.
- Possivel `pytest`/`ruff` em dependencia dev.

## Fase 5: Docker Local Completo

Status: concluida para simulador.

Concluido:

- Service `simulator`.
- `make docker-build`.
- `make docker-test`.
- `make docker-stream-test`.

Pendente:

- Otimizar imagem se necessario.
- Decidir estrategia de Python local 3.11 vs Docker como runtime oficial.

## Fase 6: CDC Local

Status: pendente.

Proximos passos:

- Subir `docker compose --profile cdc up -d`.
- Criar Make targets para Debezium connector.
- Validar Kafka UI e topicos.
- Confirmar eventos insert/update.

## Fase 7: Dashboard Operacional

Status: iniciada.

Concluido:

- Criar dashboard local para acompanhamento hospitalar.
- Comecar por consultas diretas no PostgreSQL.
- Adicionar auto-refresh e indicadores operacionais.

Proximos passos:

- Empacotar dashboard em Docker.
- Preparar configuracao para VPS.
- Depois decidir se o dashboard tambem precisa ler eventos Kafka.

## Fase 8: Remocao Lake/S3/Databricks

Status: concluida.

Concluido:

- Removido consumer raw para S3.
- Removidos artefatos Databricks.
- Removido profile `lake` do Compose.
- Documentacao reposicionada para VPS e dashboard operacional.

## Fase 9: VPS

Status: pendente.

Proximos passos:

- Criar `VPS_RUNBOOK.md`.
- Revisar portas expostas.
- Volumes persistentes.
- Backups e restart policy.
