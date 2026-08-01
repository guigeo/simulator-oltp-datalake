# Local Runbook

## Bootstrap

```bash
cp config/.env.example config/.env
make up
make test-connection
make reset
make counts
```

## Testes

```bash
make test
make test-integration
make stream-test
```

## Dashboard

```bash
make dashboard
```

URL local:

```text
http://127.0.0.1:8501
```

Dashboard via Docker:

```bash
make docker-dashboard-build
make docker-dashboard
make docker-dashboard-test
```

As portas publicadas pelo Docker ficam presas em `127.0.0.1`. Na VPS,
publique acesso externo somente por reverse proxy.

Porta alternativa:

```bash
make docker-dashboard DASHBOARD_PORT=8502
```

## Docker App

```bash
make docker-build
make docker-test
make docker-stream-test
```

## CDC Local

Validado localmente com Debezium, Kafka e Kafka UI.

```bash
make cdc-up
make connector-create
make connector-status
```

Os alvos `connector-*` chamam a API REST por dentro do container
`alimentador_connect`, evitando depender da porta `8083` exposta no host.

Depois de alterar `connectors/connector-oltp.json`, use:

```bash
make connector-recreate
make connector-status
```

Prova rapida do CDC:

```bash
make stream-test
make cdc-topics
make cdc-consume TOPIC=oltp.public.pacientes MESSAGES=1
```

Kafka UI:

```text
http://localhost:8088
```

## Contagens Esperadas Apos Reset

Valores aproximados/esperados:

```text
pacientes               2.000
medicos                   200
convenios                  14
pacientes_convenios     2.500
consultas               4.000
exames                  3.500
internacoes             1.200
```

## Troubleshooting

Conexao local:

```bash
make up
make test-connection
docker compose ps
docker compose logs postgres
```

CLI no container:

```bash
docker compose run --rm simulator python -m scripts.cli --help
docker compose run --rm simulator python -m scripts.cli stream --help
```
