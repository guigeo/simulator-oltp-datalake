.PHONY: install init seed stream counts reset fmt lint clean help

# Default target
help:
	@echo "Simulador OLTP Hospitalar - Comandos Disponíveis"
	@echo ""
	@echo "Instalação:"
	@echo "  make install          - Cria venv e instala dependências"
	@echo ""
	@echo "Banco de Dados:"
	@echo "  make init             - Inicializa schema, índices e lookups"
	@echo "  make seed             - Popula dados iniciais (≥1000 por tabela)"
	@echo "  make reset            - Drop + Recreate + Seed (cuidado!)"
	@echo "  make counts           - Exibe contagem de registros por tabela"
	@echo ""
	@echo "Streaming:"
	@echo "  make stream           - Inicia inserção contínua"
	@echo ""
	@echo "Utilitários:"
	@echo "  make fmt              - Formata código (ruff + black)"
	@echo "  make lint             - Lint (ruff check)"
	@echo "  make clean            - Remove arquivos temporários"
	@echo ""

# Instalação
install:
	python -m venv .venv && \
	. .venv/bin/activate && \
	pip install --upgrade pip && \
	pip install -r requirements.txt
	@echo "✓ Ambiente virtual criado e dependências instaladas."

# Inicialização
init:
	@. .venv/bin/activate && python -m scripts.cli init-db-cmd

seed:
	@. .venv/bin/activate && python -m scripts.cli seed

reset:
	@. .venv/bin/activate && python -m scripts.cli reset

counts:
	@. .venv/bin/activate && python -m scripts.cli counts

# Stream
stream:
	@. .venv/bin/activate && python -m scripts.cli stream

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
