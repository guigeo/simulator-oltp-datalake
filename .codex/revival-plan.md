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
- Perfis `cdc`, `lake` e `simulator` separados.

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

## Fase 7: Raw Consumer

Status: pendente.

Proximos passos:

- Refatorar `consumer_universal.py`.
- Remover credenciais hardcoded/ambiguous.
- Definir formato raw oficial, preferencialmente JSON Lines.
- Testar localmente antes de S3 real.

## Fase 8: Databricks Bronze

Status: pendente.

Proximos passos:

- Corrigir parsing conforme formato raw final.
- Adicionar tabela `convenios`.
- Tipar ids/timestamps.

## Fase 9: VPS

Status: pendente.

Proximos passos:

- Criar `VPS_RUNBOOK.md`.
- Revisar portas expostas.
- Volumes persistentes.
- Backups e restart policy.

