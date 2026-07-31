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
make stream-test
```

## Docker App

```bash
make docker-build
make docker-test
make docker-stream-test
```

## CDC Local

Ainda pendente de validacao completa.

```bash
docker compose --profile cdc up -d
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  --data @connectors/connector-oltp.json
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

