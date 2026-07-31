# Workflow

## Padrao de Trabalho

1. Entender o estado com `git status --short --branch`.
2. Fazer mudancas pequenas.
3. Rodar testes unitarios.
4. Rodar smoke test se mexeu em stream/DB.
5. Atualizar docs quando comandos/fluxos mudarem.
6. Commitar por fase.

## Validacao Basica

```bash
make test
git diff --check
```

## Validacao Com Banco Local

```bash
make up
make test-connection
make counts
make stream-test
```

Use `make reset` apenas quando o usuario autorizar recriar os dados.

## Validacao Docker

```bash
docker compose --profile simulator config --services
make docker-build
make docker-test
make docker-stream-test
```

## Antes de Commitar

```bash
git status --short --branch
git diff --stat
make test
git diff --check
```

Se mexeu em Docker:

```bash
make docker-test
```

