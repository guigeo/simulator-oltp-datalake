.PHONY: install up down ps logs docker-build docker-init docker-reset docker-stream docker-stream-test docker-test init seed stream stream-test counts reset test test-connection fmt lint clean help

PYTHON ?= python3
VENV_PYTHON := .venv/bin/python

# Default target
help:
	@echo "Simulador OLTP Hospitalar - Comandos Disponíveis"
	@echo ""
	@echo "Instalação:"
	@echo "  make install          - Cria venv e instala dependências"
	@echo ""
	@echo "Banco de Dados:"
	@echo "  make up               - Sobe PostgreSQL local"
	@echo "  make down             - Para serviços Docker"
	@echo "  make ps               - Lista serviços Docker"
	@echo "  make logs             - Acompanha logs do PostgreSQL"
	@echo "  make init             - Inicializa schema, índices e lookups"
	@echo "  make seed             - Popula dados iniciais (≥1000 por tabela)"
	@echo "  make reset            - Drop + Recreate + Seed (cuidado!)"
	@echo "  make counts           - Exibe contagem de registros por tabela"
	@echo "  make test-connection  - Testa conexão com PostgreSQL"
	@echo "  make test             - Executa testes unitários"
	@echo ""
	@echo "Streaming:"
	@echo "  make stream           - Inicia inserção contínua"
	@echo "  make stream-test      - Executa 5 ciclos de stream"
	@echo ""
	@echo "Docker App:"
	@echo "  make docker-build     - Builda imagem do simulador"
	@echo "  make docker-reset     - Recria e popula banco via container"
	@echo "  make docker-stream    - Stream contínuo via container"
	@echo "  make docker-stream-test - Executa 5 ciclos via container"
	@echo "  make docker-test      - Executa testes via container"
	@echo ""
	@echo "Utilitários:"
	@echo "  make fmt              - Formata código (ruff + black)"
	@echo "  make lint             - Lint (ruff check)"
	@echo "  make clean            - Remove arquivos temporários"
	@echo ""

# Instalação
install:
	$(PYTHON) -m venv .venv && \
	. .venv/bin/activate && \
	pip install --upgrade pip && \
	pip install -r requirements.txt
	@echo "✓ Ambiente virtual criado e dependências instaladas."

up:
	docker compose up -d postgres

down:
	docker compose down

ps:
	docker compose ps

logs:
	docker compose logs -f postgres

docker-build:
	docker compose build simulator

docker-init:
	docker compose run --rm simulator python -m scripts.cli init-db-cmd

docker-reset:
	docker compose run --rm simulator python -m scripts.cli reset

docker-stream:
	docker compose run --rm simulator python -m scripts.cli stream

docker-stream-test:
	docker compose run --rm simulator python -m scripts.cli stream --interval 1 --cycles 5

docker-test:
	docker compose run --rm simulator python -m unittest discover -s tests -p 'test_*.py'

# Inicialização
init:
	@$(VENV_PYTHON) -m scripts.cli init-db-cmd

seed:
	@$(VENV_PYTHON) -m scripts.cli seed

reset:
	@$(VENV_PYTHON) -m scripts.cli reset

counts:
	@$(VENV_PYTHON) -m scripts.cli counts

# Stream
stream:
	@$(VENV_PYTHON) -m scripts.cli stream

stream-test:
	@$(VENV_PYTHON) -m scripts.cli stream --interval 1 --cycles 5

test-connection:
	@$(VENV_PYTHON) test_connection.py

test:
	@$(VENV_PYTHON) -m unittest discover -s tests -p 'test_*.py'

# Code quality
fmt:
	@. .venv/bin/activate && \
	(ruff check --fix . || true) && \
	(black . || true)
	@echo "✓ Código formatado."

lint:
	@. .venv/bin/activate && ruff check .

# Limpeza
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .venv
	@echo "✓ Ambiente limpo."

# Aliases práticos
.venv:
	make install
