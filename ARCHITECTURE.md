# Architecture

## Overview

O sistema segue uma arquitetura modular com camadas bem definidas:

```
┌─────────────────────────────────────────┐
│          CLI (Typer)                    │
│  init-db | seed | stream | reset        │
└──────────────┬──────────────────────────┘
               │
┌──────────────┴──────────────────────────┐
│     Stream Loop (Realtime Events)       │
│  Inserções/Atualizações contínuas       │
└──────────────┬──────────────────────────┘
               │
┌──────────────┴──────────────────────────┐
│      Data Generation & Validators       │
│    generate_* + Validação de FKs        │
└──────────────┬──────────────────────────┘
               │
┌──────────────┴──────────────────────────┐
│        PostgreSQL Connection            │
│  psycopg2 + Pooling + Error Handling    │
└──────────────┴──────────────────────────┘
               │
┌──────────────┴──────────────────────────┐
│      PostgreSQL OLTP Database           │
│   7 Tabelas + Triggers + Índices        │
└─────────────────────────────────────────┘
```

## Módulos

### `cli.py`
Interface de linha de comando com Typer. Expõe 5 comandos principais:
- `init-db-cmd`: Inicializa schema
- `seed`: População inicial
- `stream`: Streaming contínuo
- `reset`: Reset completo
- `counts`: Contagens

### `db_init.py`
Gerenciamento de conexão e inicialização:
- `load_env()`: Carrega variáveis de ambiente
- `create_connection()`: Pool de conexão PostgreSQL
- `test_connection()`: Valida conectividade
- `init_db()`: Cria schema, índices, seed
- `get_table_counts()`: Query de contagens

### `stream.py`
Motor de streaming contínuo com operações realistas:

**Operações INSERT (70%)**:
- `insert_paciente()`: Novo paciente
- `insert_consulta()`: Nova consulta
- `insert_exame()`: Novo exame
- `insert_internacao()`: Nova internação

**Operações UPDATE (30%)**:
- `update_paciente()`: Atualiza telefone/endereço
- `update_consulta()`: Muda status
- `update_exame()`: Preenche resultado
- `update_internacao()`: Marca alta

**Loop Principal**:
```python
while not should_stop:
    event = random.choices(events, weights=weights)[0]
    # Execute operação...
    logger.info(f"[{cycle}] {op_type} {table} | INSERT: {total_ins} | UPDATE: {total_upd}")
    time.sleep(interval + jitter)
```

### `seed.py`
Popula dados iniciais com volumes configuráveis:
- `seed_medicos()`: 200 médicos
- `seed_pacientes()`: 2000 pacientes
- `seed_convenios()`: 12 convênios
- `seed_consultas()`: 4000 consultas
- `seed_exames()`: 3500 exames
- `seed_internacoes()`: 1200 internações
- `seed_pacientes_convenios()`: 2500 relacionamentos

Usa `execute_values()` para performance em batch.

### `data_gen.py`
Geradores de dados realistas com Faker pt_BR:
- `generate_cpf()`: CPF validado
- `generate_crm()`: CRM 6 dígitos + UF
- `generate_cnpj()`: CNPJ validado
- `generate_paciente()`: Paciente completo
- `generate_medico()`: Médico com especialidade
- `generate_convenio()`: Convênio
- `generate_consulta()`: Consulta com status ponderado
- `generate_exame()`: Exame
- `generate_internacao()`: Internação com 70% com alta

### `validators.py`
Validações e cache de FKs:
- LRU Cache com 512 entradas
- `get_random_paciente_id()`: Seleciona paciente aleatório
- `get_random_medico_id()`: Seleciona médico aleatório
- `get_random_convenio_id()`: Seleciona convênio aleatório
- `clear_cache()`: Invalida cache após mudanças

## Schema

### Pacientes
```sql
CREATE TABLE pacientes (
  id BIGSERIAL PRIMARY KEY,
  nome VARCHAR(150) NOT NULL,
  nascimento DATE NOT NULL,
  cpf VARCHAR(20) UNIQUE NOT NULL,
  telefone VARCHAR(20),
  endereco VARCHAR(200),
  data_cadastro TIMESTAMP NOT NULL DEFAULT now(),
  created_at TIMESTAMP NOT NULL DEFAULT now(),
  updated_at TIMESTAMP NOT NULL DEFAULT now()
);
CREATE TRIGGER pacientes_updated_at BEFORE UPDATE...
CREATE INDEX idx_pacientes_cpf ON pacientes (cpf);
```

### Relacionamentos
- `pacientes_convenios`: N:N com UNIQUE (paciente_id, convenio_id)
- FKs: ON UPDATE CASCADE, ON DELETE RESTRICT
- Todos com PK BIGSERIAL

## Data Flow

### Insert Operação

```
stream.py: insert_paciente()
    ↓
data_gen.py: generate_paciente()
    ↓
faker: name(), date_of_birth(), phone_number(), address()
    ↓
stream.py: cur.execute(INSERT...)
    ↓
PostgreSQL: Trigger atualiza updated_at
    ↓
validators.py: clear_cache()
```

### Update Operação

```
stream.py: update_paciente()
    ↓
validators.py: get_random_paciente_id() (com cache)
    ↓
faker: phone_number() ou address()
    ↓
stream.py: cur.execute(UPDATE...)
    ↓
PostgreSQL: Trigger atualiza updated_at
```

## Error Handling

### Reconexão
```python
except psycopg2.OperationalError:
    for attempt in range(1, 6):
        time.sleep(2 ** (attempt - 1))  # Backoff exponencial: 1s, 2s, 4s, 8s, 16s
        try:
            conn = create_connection(load_env())
            if test_connection(conn):
                validators = Validators(conn)
                break
        except Exception:
            if attempt == 5:
                should_stop = True
```

### Integrity Errors
```python
except psycopg2.IntegrityError:
    conn.rollback()
    logger.debug("CPF duplicado ao inserir paciente.")
    return False
```

## Logging

Estrutura de logs por módulo:

```
scripts.cli          → CLI entry points
scripts.db_init      → Conexão e inicialização
scripts.seed         → Operações de seed
scripts.stream       → Streaming contínuo
scripts.data_gen     → (apenas erros)
scripts.validators   → (apenas cache)
```

Rotação automática com `RotatingFileHandler` (7 dias de backups).

## Performance

### Otimizações

1. **Batch Insert**: `execute_values()` em seed
2. **LRU Cache**: 512 entradas para FK validation
3. **Jitter Aleatório**: Distribui carga uniformemente
4. **RANDOM() Limit 1**: Queries eficientes de seleção

### Volumes

- Seed: ~13k registros em <2 segundos
- Stream: ~1 operação a cada 2 segundos + jitter
- Throughput esperado: 30 ops/minuto em produção

## CDC Compatibility

O schema é totalmente compatível com Debezium:

1. **Primary Keys**: BIGSERIAL em todas as tabelas
2. **Natural Keys**: UNIQUE em CPF, CRM, CNPJ
3. **Audit Trail**: created_at, updated_at com triggers
4. **Foreign Keys**: Estratégicas para consistency
5. **Indexes**: Otimizados para WAL scanning

Configuração Debezium recomendada:
```json
{
  "plugin.name": "pgoutput",
  "table.include.list": "public.*",
  "publication.name": "alimentador_pub"
}
```

## Testing Scenarios

### 1. Volume Testing
```bash
timeout 300 make stream  # 5 minutos
make counts             # Validar crescimento
```

### 2. Consistency Testing
```sql
SELECT COUNT(*) FROM consultas WHERE paciente_id NOT IN (SELECT id FROM pacientes);
-- Deve retornar 0
```

### 3. CDC Sync Testing
- Debezium captura eventos
- Validar changelog tem INSERT/UPDATE completos
- Verificar updated_at reflete mudanças

### 4. Stress Testing
```bash
STREAM_INTERVAL_SECONDS=0 timeout 60 make stream
```
