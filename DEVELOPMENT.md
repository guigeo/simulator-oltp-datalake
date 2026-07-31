# Development Guide

This guide is for developers who want to contribute to the project or set up a local development environment.

## Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Git
- Make

## Setup

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/alimentador-bd.git
cd alimentador-bd
```

### 2. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
make install
# or
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp config/.env.example config/.env
```

For local Docker, the defaults in `config/.env.example` are enough:

```env
PG_HOST=localhost
PG_PORT=5432
PG_USER=app
PG_PASSWORD=app123
PG_DATABASE=teste_pacientes
```

`config/.env` is the official app config file. Avoid using a root `.env` for simulator settings.

### 5. Start PostgreSQL and Initialize Database

```bash
make up
make test-connection
make reset
```

## Development Workflow

### Running Tests

```bash
# Unit tests
make test

# Validate database connection
make test-connection

# Check table counts
make counts
```

### Starting Stream

```bash
# 5-cycle smoke test
make stream-test

# Continuous stream
make stream

# Custom bounded run
.venv/bin/python -m scripts.cli stream --interval 1 --cycles 30
```

### Code Quality

```bash
# Format code
make fmt

# Lint check
make lint

# Clean cache
make clean
```

## Project Structure

```
scripts/          # Python modules
sql/              # SQL scripts
config/           # Configuration
tests/            # Unit tests
Makefile          # Build targets
requirements.txt  # Dependencies
```

## Code Style

- **Line length**: 88 characters (Black compatible)
- **Type hints**: Required for all functions
- **Docstrings**: Required for public functions
- **Imports**: stdlib, third-party, local (organized)

## Adding Features

### Process

1. Fork repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Make changes following code style
4. Test thoroughly: `make test && make stream-test`
5. Commit with clear message
6. Push and create Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Debugging

### Enable Debug Logging

```python
import logging
logging.getLogger("scripts").setLevel(logging.DEBUG)
```

### Inspect Database

```bash
psql -U app -h localhost -d teste_pacientes
```

## Common Issues

### "psycopg2.OperationalError: connection refused"

Check PostgreSQL is running and credentials are correct:

```bash
make up
make test-connection
```

### "Stream stops after few events"

Check logs:
```bash
tail -f logs/app.log
```

## Performance

### Time operations

```bash
time make seed
```

Expected: ~2-5 seconds for 13k records.

## Resources

- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical design
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
