# Contributing

Contribuições são bem-vindas! Por favor, siga estas diretrizes.

## Development Setup

```bash
# Clone
git clone <repo>
cd alimentador_bd

# Ambiente
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows

# Dependências
pip install -r requirements.txt
pip install -e .
```

## Code Style

- PEP 8 com 88 caracteres de limite
- Type hints obrigatórios
- Docstrings em todas as funções públicas

```bash
# Formatar
make fmt

# Verificar
make lint
```

## Testing

```bash
make init
make seed
timeout 60 make stream
make counts
```

## Pull Requests

1. Fork o repositório
2. Crie uma branch (`git checkout -b feature/xyz`)
3. Commit com mensagens claras
4. Push e abra um PR
5. Descreva as mudanças

## Issues

- Use templates claros
- Inclua versão do Python e PostgreSQL
- Descreva passos para reproduzir
- Anexe logs relevantes
