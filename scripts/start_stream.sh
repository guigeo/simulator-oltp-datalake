#!/usr/bin/env bash
set -e

# Diretório raiz do projeto (baseado no local do script)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$PROJECT_ROOT"

# Carrega variáveis de ambiente
if [ ! -f ".env" ]; then
  echo "❌ Arquivo .env não encontrado no diretório do projeto"
  exit 1
fi

export $(cat .env | xargs)

echo "🚀 Iniciando make stream..."
exec make stream
