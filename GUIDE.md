# 📘 Guia Completo - Simulador OLTP Hospitalar CDC

> **Tudo que você precisa saber para usar este projeto em um único arquivo.**

---

## 📖 Índice

1. [O Que É](#o-que-é)
2. [Estrutura](#estrutura)
3. [Pré-requisitos](#pré-requisitos)
4. [Instalação & Configuração](#instalação--configuração)
5. [Passo-a-Passo de Execução](#passo-a-passo-de-execução)
6. [Comandos Disponíveis](#comandos-disponíveis)
7. [Geração de Dados](#geração-de-dados)
8. [Observabilidade & Logs](#observabilidade--logs)
9. [Troubleshooting](#troubleshooting)
10. [Referência Técnica](#referência-técnica)

---

## O Que É?

**Simulador OLTP Hospitalar** é uma automação em Python que simula inserções contínuas em um banco PostgreSQL com estrutura hospitalar realista, ideal para testes de **CDC (Change Data Capture)** via Debezium.

### Características Principais
- ✅ **Inserção contínua** com intervalo configurável e jitter aleatório
- ✅ **7 tabelas OLTP** com 13.000+ registros iniciais
- ✅ **Geração de dados** com Faker (locale pt_BR)
- ✅ **CLI Typer** com 5 comandos prontos
- ✅ **Resiliente** com reconexão automática
- ✅ **Observável** com logs estruturados
- ✅ **CDC-ready** para Debezium

---

## Estrutura

```
alimentador_bd/
├── config/
│   ├── .env                    ← Seu arquivo de credenciais
│   ├── .env.example            ← Template
│   └── settings.toml           ← Configurações
├── sql/
│   ├── 01_schema.sql           ← Schema (7 tabelas)
│   ├── 02_indexes.sql          ← Índices (9)
│   ├── 03_seed-lookups.sql     ← Dados iniciais
│   └── 99_drop_all.sql         ← Limpeza
├── scripts/
│   ├── cli.py                  ← CLI Typer (5 comandos)
│   ├── db_init.py              ← Conexão + init
│   ├── seed.py                 ← Seed functions
│   ├── stream.py               ← Streaming contínuo
│   ├── reset.py                ← Reset total
│   ├── data_gen.py             ← Faker generators
│   ├── validators.py           ← Validação + cache LRU
│   └── __init__.py
├── logs/                       ← Gerado em runtime
├── test_connection.py          ← Teste de conexão
├── requirements.txt            ← Dependências
├── Makefile                    ← Atalhos
├── .gitignore
├── AGENTS.md                   ← Especificação (referência)
└── GUIDE.md                    ← Este arquivo
```

---

## Pré-requisitos

### Essencial
- **Python 3.11+** instalado
- **PostgreSQL 14+** rodando em `10.42.88.67:5441`
- **Credenciais**: usuário `app` / senha `app123` / banco `postgres`

### Verificar Pré-requisitos
```bash
# Python
python --version

# PostgreSQL (se remoto)
telnet 10.42.88.67 5441  # Ctrl+] then quit (ou Ctrl+C)
```

---

## Instalação & Configuração

### 1️⃣ Clonar/Acessar o Projeto
```bash
cd /home/henrique.ferreira/workspace/alimentador_bd
```

### 2️⃣ Copiar Arquivo de Ambiente
```bash
cp config/.env.example config/.env
```

**Verificar que `.env` contém:**
```env
PG_HOST=10.42.88.67
PG_PORT=5441
PG_USER=app
PG_PASSWORD=app123
PG_DATABASE=postgres
```

### 3️⃣ Testar Conexão
```bash
# Instalar dependências mínimas
pip install python-dotenv psycopg2-binary

# Executar teste
python test_connection.py
```

**Saída esperada:**
```
✅ Conexão estabelecida com sucesso!
✅ Query executada: SELECT 1
✅ PostgreSQL Info: PostgreSQL 14.x...
✨ TUDO OK! Pronto para usar.
```

### 4️⃣ Instalar Dependências Completas
```bash
make install

# Ou manualmente:
# python -m venv .venv
# source .venv/bin/activate  (Windows: .venv\Scripts\activate)
# pip install -r requirements.txt
```

**Dependências instaladas:**
- psycopg2-binary (driver PostgreSQL)
- python-dotenv (arquivo .env)
- typer (CLI)
- faker (geração de dados)
- pydantic (validação)

---

## Passo-a-Passo de Execução

### 📍 Passo 1: Inicializar Banco de Dados

Cria o schema, índices e dados de lookup iniciais.

```bash
make init
```

**O que acontece:**
- ✓ Cria 7 tabelas (pacientes, medicos, convenios, etc.)
- ✓ Cria 7 triggers para `updated_at`
- ✓ Cria 9 índices estratégicos
- ✓ Carrega 2 convênios iniciais (SUS, SaudePlus)

**Tempo:** ~3-5 segundos

---

### 📍 Passo 2: Popular com Dados Iniciais

Popula ~13.000 registros nas 7 tabelas usando Faker pt_BR.

```bash
make seed
```

**O que acontece:**
```
Médicos: +50 (total=200)
Pacientes: +50 (total=2000)
Convenios: +12 (total=12)
Pacientes_Convênios: +50 (total=2500)
Consultas: +50 (total=4000)
Exames: +50 (total=3500)
Internações: +50 (total=1200)
```

**Tempo:** ~2-5 minutos (depende da rede)

**Volumes Finais:**
| Tabela | Registros |
|--------|-----------|
| pacientes | 2.000 |
| medicos | 200 |
| convenios | 12 |
| pacientes_convenios | ~2.500 |
| consultas | 4.000 |
| exames | 3.500 |
| internacoes | 1.200 |
| **TOTAL** | **~13.000** |

---

### 📍 Passo 3: Iniciar Streaming Contínuo

Inicia inserção contínua de eventos (consultas, exames, internações, novos pacientes).

```bash
make stream
```

**O que acontece:**
- ✓ Insere eventos continuamente (intervalo 2s + jitter)
- ✓ Mix realista: 55% consulta, 25% exame, 15% internação, 10% paciente
- ✓ Validação de FKs com cache LRU
- ✓ Transações seguras com commit/rollback
- ✓ Logs em console + arquivo

**Saída esperada:**
```
INFO ... Iniciando stream com intervalo 2s e jitter até 400ms
DEBUG ... Novo paciente inserido.
DEBUG ... Consulta inserida: 1234
INFO ... Stream ciclo 50: consultas: 27 | exames: 12 | internacoes: 7 | pacientes: 4
```

**Parar o stream:**
```
Ctrl+C
```

---

### 📍 Passo 4 (Opcional): Monitorar em Tempo Real

Em **outro terminal**, execute:

```bash
# Ver contagens atualizadas a cada 5s
watch -n 5 'python -m scripts.cli counts'

# Ou manualmente:
python -m scripts.cli counts
```

**Saída esperada:**
```
=== Contagem de Registros ===
pacientes..................... 2,000
medicos......................    200
convenios.....................     12
pacientes_convenios........  2,500
consultas.................  4,100  (crescendo!)
exames....................  3,600  (crescendo!)
internacoes...............  1,250  (crescendo!)
───────────────────────────────────
TOTAL....................  13,162+
```

---

### 📍 Passo 5 (Opcional): Reset Total

**⚠️ CUIDADO: Deleta todos os dados!**

```bash
make reset
```

Confirmará antes de executar. Depois recria schema e popula novamente.

---

## Comandos Disponíveis

### Via Makefile (Recomendado)

```bash
make init              # Criar schema + índices + lookups
make seed              # Popular dados iniciais (~13.000)
make stream            # Inserção contínua
make reset             # Drop + recreate + seed
make counts            # Ver contagens
make fmt               # Formatar código (ruff + black)
make lint              # Verificar código (ruff)
make clean             # Remover venv + __pycache__
make help              # Ver ajuda
```

### Via Python (Direto)

```bash
# Ativar venv primeiro
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Comandos
python -m scripts.cli init-db-cmd
python -m scripts.cli seed [--volume 2]
python -m scripts.cli stream [--interval 2] [--batch-size 50]
python -m scripts.cli reset
python -m scripts.cli counts

# Teste de conexão
python test_connection.py
```

---

## Geração de Dados

### Faker pt_BR

Usa **Faker com locale pt_BR** para gerar dados realistas em português:

```python
# Exemplos
CPF:      123.456.789-00 (com validação de dígitos)
CRM:      123456SP (6 dígitos + 2 letras UF)
CNPJ:     12.345.678/0001-99 (com validação)
Nomes:    João da Silva, Maria Santos (português)
Telefone: (11) 98765-4321
Endereço: Rua das Flores, 123 - São Paulo, SP
```

### Volumes Padrão

Configuráveis em `config/.env`:

```env
SEED_PACIENTES=2000
SEED_MEDICOS=200
SEED_CONVENIOS=12
SEED_CONSULTAS=4000
SEED_EXAMES=3500
SEED_INTERNACOES=1200
SEED_PACIENTES_CONVENIOS=2500
```

### Status e Tipos

**Status de Consulta** (distribuição ponderada):
- 55% = `agendada`
- 35% = `realizada`
- 5% = `cancelada`
- 5% = `faltou`

**Tipos de Exame:**
- Hemograma, Raio-X, Tomografia, Ultrassom, PCR, ECG, etc.

**Internações:**
- 70% com `data_saida` (alta hospitalar)
- 30% sem `data_saida` (ainda internado)

---

## Observabilidade & Logs

### Arquivos de Log

Gerados em `/logs`:
```
app.log        → Log geral (init, seed, CLI)
stream.log     → Log específico do stream
errors.log     → Apenas erros
```

### Ver Logs em Tempo Real

```bash
# Log geral
tail -f logs/app.log

# Apenas erros
grep "ERROR" logs/app.log
tail -f logs/app.log | grep "ERROR\|WARNING"

# Todos os logs
ls -la logs/
```

### Formato de Log

```
2025-11-05 14:23:45,123 INFO oltp.simulator [seed_medicos] - Médicos: +50 (total=200)
```

### Contadores por Ciclo

A cada 50 ciclos do stream, exibe:
```
INFO ... Stream ciclo 50: consultas: 27 | exames: 12 | internacoes: 7 | pacientes: 4
```

---

## Troubleshooting

### ❌ Erro: "Conexão recusada"

**Problema:** `psycopg2.OperationalError: could not connect to server`

**Verificar:**
```bash
# Testar IP/porta
ping 10.42.88.67
telnet 10.42.88.67 5441

# Ou via Python
python test_connection.py

# Manualmente com psql
psql -h 10.42.88.67 -p 5441 -U app -d postgres -c "SELECT 1"
```

---

### ❌ Erro: "Database não existe"

**Problema:** `database "postgres" does not exist`

**Solução:**
```bash
# Criar banco (se for necessário)
createdb -U app -h 10.42.88.67 -p 5441 postgres

# Ou mudar em config/.env para outro banco existente
PG_DATABASE=seu_banco_existente
```

---

### ❌ Erro: "Módulo não encontrado"

**Problema:** `ModuleNotFoundError: No module named 'typer'`

**Solução:**
```bash
# Reinstalar dependências
pip install -r requirements.txt

# Ou via venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

### ❌ Aviso: "CPF duplicado"

**Problema:** Alguns registros não são inseridos durante seed

**Causa:** Com Faker, volumes altos podem gerar duplicatas

**É normal!** O sistema ignora automaticamente.

**Ver logs:**
```bash
grep "CPF duplicado\|IntegrityError" logs/*.log
```

---

### ❌ Stream para após alguns eventos

**Problema:** Inserção funciona poucos segundos depois para

**Verificar:**
1. Logs: `tail -f logs/app.log`
2. Conexão: `python test_connection.py`
3. Dados: `python -m scripts.cli counts`
4. Reseedie se vazio: `make seed`

---

### ❌ Stream muito lento

**Problema:** Inserindo 1-2 registros/segundo

**Soluções:**
```bash
# 1. Reduzir intervalo
STREAM_INTERVAL_SECONDS=0.5

# 2. Aumentar batch
BATCH_SIZE=100

# 3. Otimizar índices
psql -h 10.42.88.67 -p 5441 -U app -d postgres -f sql/02_indexes.sql
```

---

## Referência Técnica

### Schema OLTP (7 Tabelas)

#### pacientes
```sql
id (BIGSERIAL PK) | nome | nascimento | cpf (UK) | telefone 
endereco | data_cadastro | created_at | updated_at
```

#### medicos
```sql
id (BIGSERIAL PK) | nome | crm (UK) | especialidade | telefone 
created_at | updated_at
```

#### convenios
```sql
id (BIGSERIAL PK) | nome | cnpj (UK) | tipo | cobertura 
created_at | updated_at
```

#### pacientes_convenios (N:N)
```sql
id (BIGSERIAL PK) | paciente_id (FK) | convenio_id (FK) 
numero_carteira | validade | created_at | updated_at
(UK: paciente_id, convenio_id)
```

#### consultas
```sql
id (BIGSERIAL PK) | paciente_id (FK) | medico_id (FK) | data 
motivo | status (CHECK) | created_at | updated_at
```

#### exames
```sql
id (BIGSERIAL PK) | paciente_id (FK) | tipo_exame | data 
resultado | created_at | updated_at
```

#### internacoes
```sql
id (BIGSERIAL PK) | paciente_id (FK) | data_entrada | data_saida 
motivo | quarto | created_at | updated_at
(CHECK: data_saida >= data_entrada)
```

### Constraints

- **PK:** BIGSERIAL em todas as tabelas
- **UK:** CPF, CRM, CNPJ (únicos)
- **FK:** ON UPDATE CASCADE, ON DELETE RESTRICT
- **Triggers:** updated_at automático em UPDATE

### Índices (9)

```sql
idx_pacientes_cpf
idx_medicos_crm
idx_consultas_paciente
idx_consultas_medico
idx_consultas_data
idx_exames_paciente
idx_exames_data
idx_internacoes_paciente
idx_internacoes_datas
```

---

### Dependências Python

```
psycopg2-binary==2.9.9      (driver PostgreSQL)
python-dotenv==1.0.0        (arquivo .env)
typer==0.12.3               (CLI)
faker==21.0.0               (geração de dados)
pydantic==2.5.0             (validação)
```

---

### Volumes e Performance

| Operação | Tempo | Volume |
|----------|-------|--------|
| Init DB | 3-5s | Schema + triggers + índices |
| Seed | 2-5m | ~13.000 registros |
| Stream (1 evento) | 100-500ms | 1 INSERT em transação |
| Stream (1 min) | 1m | ~30-50 eventos |
| Stream (1 hora) | 1h | ~2.000-3.000 eventos |
| Stream (1 dia) | 1d | ~50.000+ eventos |

---

### Configurações (config/.env)

```env
# Conexão
PG_HOST=10.42.88.67
PG_PORT=5441
PG_USER=app
PG_PASSWORD=app123
PG_DATABASE=postgres

# Stream
STREAM_INTERVAL_SECONDS=2        (intervalo em segundos)
BATCH_SIZE=50                     (registros por batch)
MAX_JITTER_MS=400                 (variação aleatória em ms)

# Seed
SEED_PACIENTES=2000
SEED_MEDICOS=200
SEED_CONVENIOS=12
SEED_CONSULTAS=4000
SEED_EXAMES=3500
SEED_INTERNACOES=1200
SEED_PACIENTES_CONVENIOS=2500

# Logs
LOG_LEVEL=INFO
```

---

### Eventos do Stream (Distribuição)

```
10% = Novo paciente
55% = Nova consulta
25% = Novo exame
15% = Nova internação
───────
100% = Total por ciclo
```

### Cache LRU (Validators)

```
check_paciente_exists()   → 512 entradas
check_medico_exists()     → 512 entradas
check_convenio_exists()   → 512 entradas
```

Invalida automaticamente após cada INSERT de novo paciente/médico/convênio.

---

## Próximos Passos

### Para CDC/Debezium

1. ✅ Dados populados? Verifique com `make counts`
2. ✅ Stream rodando? Observe em `tail -f logs/app.log`
3. ➡️ **Habilite WAL logging** no PostgreSQL
4. ➡️ **Configure Debezium** para capturar eventos
5. ➡️ **Envie para Kafka/Pulsar** ou destino

### Validações Sugeridas

- Todos os eventos foram capturados?
- Consistência de dados (origem vs destino)?
- Performance de CDC?
- Failover e recovery?

---

## Referências Rápidas

### Comandos Úteis

```bash
# Testar conexão
python test_connection.py

# Ver contagens
python -m scripts.cli counts

# Limpar venv
make clean

# Formatar código
make fmt

# Ver ajuda
make help
```

### Arquivos Importantes

| Arquivo | Propósito |
|---------|-----------|
| `config/.env` | Suas credenciais (NÃO commitar!) |
| `config/.env.example` | Template seguro (OK commitar) |
| `sql/01_schema.sql` | Schema principal |
| `scripts/cli.py` | CLI Typer |
| `scripts/stream.py` | Inserção contínua |
| `scripts/data_gen.py` | Geradores Faker |
| `requirements.txt` | Dependências |
| `Makefile` | Atalhos de comando |

---

## FAQ

### P: Posso pausar e retomar o stream?
**R:** Sim! Use `Ctrl+C` para parar. Execute `make stream` novamente para retomar.

### P: Como aumentar o volume?
**R:** Edite `config/.env` e altere os valores `SEED_*`. Depois execute `make seed` novamente.

### P: Stream está lento?
**R:** Reduza `STREAM_INTERVAL_SECONDS` ou aumente `BATCH_SIZE` em `config/.env`.

### P: Como resetar tudo?
**R:** Execute `make reset` (cuidado - deleta dados!).

### P: Que versão de PostgreSQL é necessária?
**R:** PostgreSQL 14+, idealmente com WAL logging habilitado para CDC.

### P: Posso usar localmente?
**R:** Sim! Mude `config/.env` para:
```env
PG_HOST=localhost
PG_PORT=5432
PG_USER=postgres
PG_PASSWORD=postgres
```

---

## Suporte & Contato

- **Código:** Todos os 29 arquivos prontos para usar
- **Documentação:** Este guia + AGENTS.md (especificação)
- **Logs:** Verifique `/logs` para diagnóstico
- **Teste:** Use `python test_connection.py` para validar

---

## Licença

Código livre para uso em testes de CDC/Debezium.

---

**Última atualização:** 5 de novembro de 2025

✨ **Bom desenvolvimento!** 🚀
