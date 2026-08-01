"""
Seed: popula o banco com volume inicial de dados.
"""

import logging
import os
from datetime import datetime
from typing import Callable, Optional

import psycopg2
from psycopg2.extras import execute_values

from scripts.data_gen import (
    generate_paciente,
    generate_medico,
    generate_convenio,
    generate_consulta,
    generate_exame,
    generate_internacao,
)
from scripts.db_init import (
    load_env,
    create_connection,
    test_connection,
    load_project_env,
)
from scripts.validators import Validators

logger = logging.getLogger(__name__)

INSERT_MEDICOS_SQL = """
INSERT INTO medicos (nome, crm, especialidade, telefone)
VALUES %s
"""

INSERT_PACIENTES_SQL = """
INSERT INTO pacientes
(nome, nascimento, cpf, telefone, endereco, data_cadastro)
VALUES %s
"""

INSERT_CONVENIOS_SQL = """
INSERT INTO convenios (nome, cnpj, tipo, cobertura)
VALUES %s
"""

INSERT_CONSULTAS_SQL = """
INSERT INTO consultas
(paciente_id, medico_id, data, motivo, status)
VALUES %s
"""

INSERT_EXAMES_SQL = """
INSERT INTO exames
(paciente_id, tipo_exame, data, resultado)
VALUES %s
"""

INSERT_INTERNACOES_SQL = """
INSERT INTO internacoes
(paciente_id, data_entrada, data_saida, motivo, quarto)
VALUES %s
"""

INSERT_PACIENTES_CONVENIOS_SQL = """
INSERT INTO pacientes_convenios
(paciente_id, convenio_id, numero_carteira, validade)
VALUES %s
ON CONFLICT DO NOTHING
RETURNING id
"""


def flush_insert_batch(
    conn: psycopg2.extensions.connection,
    sql: str,
    batch: list[tuple],
    label: str,
    total_inserted: int,
) -> int:
    """Insere um batch, faz commit e retorna o total atualizado."""
    if not batch:
        return total_inserted

    with conn.cursor() as cur:
        execute_values(cur, sql, batch)
    conn.commit()

    total_inserted += len(batch)
    logger.info(f"{label}: +{len(batch)} (total={total_inserted})")
    return total_inserted


def seed_insert_rows(
    conn: psycopg2.extensions.connection,
    count: int,
    batch_size: int,
    sql: str,
    label: str,
    error_label: str,
    row_factory: Callable[[], Optional[tuple]],
) -> int:
    """Gera linhas e insere em batches."""
    total_inserted = 0
    batch = []

    try:
        for _ in range(count):
            row = row_factory()
            if row:
                batch.append(row)

            if len(batch) >= batch_size:
                total_inserted = flush_insert_batch(
                    conn,
                    sql,
                    batch,
                    label,
                    total_inserted,
                )
                batch = []

        return flush_insert_batch(conn, sql, batch, label, total_inserted)
    except psycopg2.Error as e:
        logger.error(f"Erro ao seed de {error_label}: {e}")
        conn.rollback()
        return total_inserted


def flush_conflict_aware_batch(
    conn: psycopg2.extensions.connection,
    sql: str,
    batch: list[tuple],
) -> int:
    """Insere batch com RETURNING e retorna quantas linhas entraram."""
    if not batch:
        return 0

    with conn.cursor() as cur:
        inserted_rows = execute_values(cur, sql, batch, fetch=True)
    conn.commit()
    return len(inserted_rows)


def load_config() -> dict:
    """Carrega configurações do .env."""
    load_project_env()
    return {
        "seed_pacientes": int(os.getenv("SEED_PACIENTES", 2000)),
        "seed_medicos": int(os.getenv("SEED_MEDICOS", 200)),
        "seed_convenios": int(os.getenv("SEED_CONVENIOS", 12)),
        "seed_consultas": int(os.getenv("SEED_CONSULTAS", 4000)),
        "seed_exames": int(os.getenv("SEED_EXAMES", 3500)),
        "seed_internacoes": int(os.getenv("SEED_INTERNACOES", 1200)),
        "seed_pacientes_convenios": int(
            os.getenv("SEED_PACIENTES_CONVENIOS", 2500)
        ),
        "batch_size": int(os.getenv("BATCH_SIZE", 50)),
    }


def seed_medicos(
    conn: psycopg2.extensions.connection,
    count: int,
    batch_size: int,
) -> int:
    """Popula tabela de médicos."""
    logger.info(f"Iniciando seed de {count} médicos...")

    def build_row() -> tuple:
        medico = generate_medico()
        return (
            medico["nome"],
            medico["crm"],
            medico["especialidade"],
            medico["telefone"],
        )

    return seed_insert_rows(
        conn,
        count,
        batch_size,
        INSERT_MEDICOS_SQL,
        "Médicos",
        "médicos",
        build_row,
    )


def seed_pacientes(
    conn: psycopg2.extensions.connection,
    count: int,
    batch_size: int,
) -> int:
    """Popula tabela de pacientes."""
    logger.info(f"Iniciando seed de {count} pacientes...")

    def build_row() -> tuple:
        paciente = generate_paciente()
        return (
            paciente["nome"],
            paciente["nascimento"],
            paciente["cpf"],
            paciente["telefone"],
            paciente["endereco"],
            paciente["data_cadastro"],
        )

    return seed_insert_rows(
        conn,
        count,
        batch_size,
        INSERT_PACIENTES_SQL,
        "Pacientes",
        "pacientes",
        build_row,
    )


def seed_convenios(
    conn: psycopg2.extensions.connection,
    count: int,
    batch_size: int,
) -> int:
    """Popula tabela de convênios."""
    logger.info(f"Iniciando seed de {count} convênios...")

    def build_row() -> tuple:
        convenio = generate_convenio()
        return (
            convenio["nome"],
            convenio["cnpj"],
            convenio["tipo"],
            convenio["cobertura"],
        )

    return seed_insert_rows(
        conn,
        count,
        batch_size,
        INSERT_CONVENIOS_SQL,
        "Convênios",
        "convênios",
        build_row,
    )


def seed_pacientes_convenios(
    conn: psycopg2.extensions.connection,
    count: int,
    batch_size: int,
) -> int:
    """Popula tabela N:N pacientes_convenios."""
    logger.info(f"Iniciando seed de {count} associações paciente-convênio...")

    total_inserted = 0
    batch = []
    validators = Validators(conn)
    max_attempts = max(count * 10, batch_size)
    attempts = 0

    def build_row() -> Optional[tuple]:
        paciente_id = validators.get_random_paciente_id()
        convenio_id = validators.get_random_convenio_id()
        if not paciente_id or not convenio_id:
            return None

        return (
            paciente_id,
            convenio_id,
            f"CARTEIRA-{paciente_id}-{convenio_id}",
            datetime.now().date(),
        )

    def flush_and_count() -> int:
        nonlocal batch
        inserted = flush_conflict_aware_batch(
            conn,
            INSERT_PACIENTES_CONVENIOS_SQL,
            batch,
        )
        batch = []
        return inserted

    try:
        while total_inserted < count and attempts < max_attempts:
            attempts += 1
            row = build_row()
            if row:
                batch.append(row)

            if len(batch) >= batch_size or total_inserted + len(batch) >= count:
                inserted = flush_and_count()
                total_inserted += inserted
                logger.info(
                    f"Pacientes_Convênios: +{inserted} (total={total_inserted})"
                )

        if batch:
            inserted = flush_and_count()
            total_inserted += inserted
            logger.info(
                f"Pacientes_Convênios: +{inserted} (total={total_inserted})"
            )

        if total_inserted < count:
            logger.warning(
                "Seed de pacientes_convenios inseriu %s/%s após %s tentativas.",
                total_inserted,
                count,
                attempts,
            )
    except psycopg2.Error as e:
        logger.error(f"Erro ao seed de pacientes_convenios: {e}")
        conn.rollback()

    return total_inserted


def seed_consultas(
    conn: psycopg2.extensions.connection,
    count: int,
    batch_size: int,
) -> int:
    """Popula tabela de consultas."""
    logger.info(f"Iniciando seed de {count} consultas...")
    validators = Validators(conn)

    def build_row() -> Optional[tuple]:
        paciente_id = validators.get_random_paciente_id()
        medico_id = validators.get_random_medico_id()
        if not paciente_id or not medico_id:
            return None

        consulta = generate_consulta(paciente_id, medico_id)
        return (
            consulta["paciente_id"],
            consulta["medico_id"],
            consulta["data"],
            consulta["motivo"],
            consulta["status"],
        )

    return seed_insert_rows(
        conn,
        count,
        batch_size,
        INSERT_CONSULTAS_SQL,
        "Consultas",
        "consultas",
        build_row,
    )


def seed_exames(
    conn: psycopg2.extensions.connection,
    count: int,
    batch_size: int,
) -> int:
    """Popula tabela de exames."""
    logger.info(f"Iniciando seed de {count} exames...")
    validators = Validators(conn)

    def build_row() -> Optional[tuple]:
        paciente_id = validators.get_random_paciente_id()
        if not paciente_id:
            return None

        exame = generate_exame(paciente_id)
        return (
            exame["paciente_id"],
            exame["tipo_exame"],
            exame["data"],
            exame["resultado"],
        )

    return seed_insert_rows(
        conn,
        count,
        batch_size,
        INSERT_EXAMES_SQL,
        "Exames",
        "exames",
        build_row,
    )


def seed_internacoes(
    conn: psycopg2.extensions.connection,
    count: int,
    batch_size: int,
) -> int:
    """Popula tabela de internações."""
    logger.info(f"Iniciando seed de {count} internações...")
    validators = Validators(conn)

    def build_row() -> Optional[tuple]:
        paciente_id = validators.get_random_paciente_id()
        if not paciente_id:
            return None

        internacao = generate_internacao(paciente_id)
        return (
            internacao["paciente_id"],
            internacao["data_entrada"],
            internacao["data_saida"],
            internacao["motivo"],
            internacao["quarto"],
        )

    return seed_insert_rows(
        conn,
        count,
        batch_size,
        INSERT_INTERNACOES_SQL,
        "Internações",
        "internações",
        build_row,
    )


def run_seed(conn: psycopg2.extensions.connection, config: dict) -> dict:
    """Executa seed em ordem e retorna resumo por tabela."""
    batch_size = config["batch_size"]
    return {
        "medicos": seed_medicos(conn, config["seed_medicos"], batch_size),
        "pacientes": seed_pacientes(conn, config["seed_pacientes"], batch_size),
        "convenios": seed_convenios(conn, config["seed_convenios"], batch_size),
        "pacientes_convenios": seed_pacientes_convenios(
            conn,
            config["seed_pacientes_convenios"],
            batch_size,
        ),
        "consultas": seed_consultas(conn, config["seed_consultas"], batch_size),
        "exames": seed_exames(conn, config["seed_exames"], batch_size),
        "internacoes": seed_internacoes(
            conn,
            config["seed_internacoes"],
            batch_size,
        ),
    }


def log_seed_summary(summary: dict) -> None:
    """Loga resumo consolidado do seed."""
    total = sum(summary.values())
    logger.info("Resumo do seed:")
    for table, inserted in summary.items():
        logger.info("  %s: %s", table, inserted)
    logger.info("Total inserido no seed: %s", total)


def main():
    """Executa seed completo."""
    config = load_config()
    env_vars = load_env()

    conn = create_connection(env_vars)
    if not test_connection(conn):
        logger.error("Falha ao testar conexão com o banco.")
        conn.close()
        return

    logger.info("Iniciando seed de dados...")
    summary = run_seed(conn, config)
    log_seed_summary(summary)
    logger.info("Seed concluído com sucesso!")
    conn.close()


if __name__ == "__main__":
    main()
