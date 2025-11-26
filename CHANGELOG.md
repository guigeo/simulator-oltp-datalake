# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-14

### Added

#### Core Features
- ✨ **Stream Engine**: Continuous INSERT/UPDATE operations with realistic distributions (70/30)
- ✨ **CLI Interface**: Typer-based command-line with 5 commands (init-db, seed, stream, reset, counts)
- ✨ **Data Generation**: Faker pt_BR for realistic Brazilian data (CPF, CNPJ, names, addresses)
- ✨ **OLTP Schema**: 7 PostgreSQL tables with proper relationships, triggers, and indexes
- ✨ **Seed Population**: ~13k initial records across all tables
- ✨ **Error Handling**: Graceful degradation with exponential backoff reconnection
- ✨ **Logging**: Comprehensive logging with file rotation and per-operation tracking

#### Operations
- 4 INSERT operations: `insert_paciente`, `insert_consulta`, `insert_exame`, `insert_internacao`
- 4 UPDATE operations: `update_paciente`, `update_consulta`, `update_exame`, `update_internacao`
- Real-time cycle tracking with operation type and total counts

#### Database Schema
- `pacientes`: 2000 base records, 70% have updated telefone/endereco
- `medicos`: 200 specialists with validated CRM
- `convenios`: 12 insurance plans with type classification
- `pacientes_convenios`: N:N relationships, 2500+ mappings
- `consultas`: 4000+ appointments with status transitions
- `exames`: 3500+ lab results with dynamic status
- `internacoes`: 1200+ hospital stays with realistic durations

#### Configuration
- `.env` support with 10+ environment variables
- `settings.toml` for structured configuration
- Configurable intervals, batch sizes, and jitter
- Log level control

#### Documentation
- `README.md`: Quick start guide and comprehensive feature documentation
- `CONTRIBUTING.md`: Development guidelines and workflow
- `ARCHITECTURE.md`: Technical architecture and data flow
- `GUIDE.md`: Detailed user guide
- `LICENSE`: MIT license

#### Build & Development
- `Makefile` with 9 targets (install, init, seed, stream, reset, counts, fmt, lint, clean)
- `requirements.txt` with 5 production dependencies
- Comprehensive `.gitignore` for Python projects
- Test connection utility

### Technical Details

#### Database
- PostgreSQL 14+ with CDC-ready schema
- Automatic `updated_at` triggers on all tables
- BIGSERIAL primary keys with unique natural keys
- Strategic indexes on CPF, CRM, foreign keys, and dates
- Cascading foreign keys with proper restrictions

#### Code Quality
- Type hints throughout codebase
- PEP 8 compliance with 88-character line limit
- Comprehensive error handling
- LRU Cache (512 entries) for FK validation
- Modular design with clear separation of concerns

#### Performance
- Batch inserts with `execute_values()` during seeding
- Jitter-based load distribution
- Efficient random selections with indexed queries
- ~1 operation per 2 seconds in streaming mode
- ~13k records seeded in <2 seconds

#### Resilience
- Automatic connection recovery with exponential backoff (1s, 2s, 4s, 8s, 16s)
- Graceful shutdown on SIGINT/SIGTERM
- Duplicate handling with logging (not failure)
- Transaction rollback on critical errors
- Continuous operation despite non-critical failures

### Fixed

- N/A (Initial release)

### Deprecated

- N/A (Initial release)

### Removed

- N/A (Initial release)

### Security

- Environment variables for sensitive credentials (.env not in git)
- SQL parameterization to prevent injection
- Masked sensitive data in logs (CPF/CNPJ patterns)

---

## Future Roadmap

### v1.1.0 (Planned)

- [ ] DELETE operations (low probability realistic deletions)
- [ ] Concurrent operation support (multiple threads)
- [ ] Prometheus metrics endpoint
- [ ] CloudWatch integration option
- [ ] Docker Compose setup
- [ ] Performance benchmarking suite

### v1.2.0 (Planned)

- [ ] Transaction simulation (multiple related inserts)
- [ ] Time travel support (backdated events)
- [ ] Custom operation weights
- [ ] Database snapshots/restore
- [ ] Debezium integration examples

### v2.0.0 (Planned)

- [ ] Multi-database support (MySQL, Oracle)
- [ ] REST API for remote control
- [ ] Web dashboard for monitoring
- [ ] Distributed streaming across nodes
- [ ] Real-time analytics queries

---

## Versioning Strategy

This project uses **Semantic Versioning**:

- **MAJOR**: Breaking changes to API or data schema
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes and improvements

---

## Git Release Tags

```bash
git tag -a v1.0.0 -m "Initial OLTP simulator release"
git push origin v1.0.0
```

---

## Migration Guide

### From Pre-1.0.0 (Development)

If you were using the development version before public release:

1. **Backup your data**:
   ```bash
   pg_dump -U app -h 10.42.88.67 -d teste_pacientes > backup.sql
   ```

2. **Reset and migrate**:
   ```bash
   make reset
   ```

3. **Verify consistency**:
   ```bash
   make counts
   ```

---

## Contributors

- **Development**: GitHub Copilot (Version 1.0.0)
- **Specification**: Henrique Ferreira

---

## Support

For issues, feature requests, or questions:

1. Check the [README.md](README.md) troubleshooting section
2. Review [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
3. Consult [GUIDE.md](GUIDE.md) for usage examples
4. Open an issue with reproduction steps
