"""
Seed: popula o banco com volume inicial de dados.
"""

import logging
import os
from datetime import datetime
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
    
    total_inserted = 0
    batch = []
    
    try:
        for _ in range(count):
            medico = generate_medico()
            batch.append(
                (
                    medico["nome"],
                    medico["crm"],
                    medico["especialidade"],
                    medico["telefone"],
                )
            )
            
            if len(batch) >= batch_size:
                total_inserted = flush_insert_batch(
                    conn,
                    INSERT_MEDICOS_SQL,
                    batch,
                    "Médicos",
                    total_inserted,
                )
                batch = []
        
        # Último batch
        if batch:
            total_inserted = flush_insert_batch(
                conn,
                INSERT_MEDICOS_SQL,
                batch,
                "Médicos",
                total_inserted,
            )
    except psycopg2.Error as e:
        logger.error(f"Erro ao seed de médicos: {e}")
        conn.rollback()
    
    return total_inserted


def seed_pacientes(
    conn: psycopg2.extensions.connection,
    count: int,
    batch_size: int,
) -> int:
    """Popula tabela de pacientes."""
    logger.info(f"Iniciando seed de {count} pacientes...")
    
    total_inserted = 0
    batch = []
    
    try:
        for _ in range(count):
            paciente = generate_paciente()
            batch.append(
                (
                    paciente["nome"],
                    paciente["nascimento"],
                    paciente["cpf"],
                    paciente["telefone"],
                    paciente["endereco"],
                    paciente["data_cadastro"],
                )
            )
            
            if len(batch) >= batch_size:
                total_inserted = flush_insert_batch(
                    conn,
                    INSERT_PACIENTES_SQL,
                    batch,
                    "Pacientes",
                    total_inserted,
                )
                batch = []
        
        # Último batch
        if batch:
            total_inserted = flush_insert_batch(
                conn,
                INSERT_PACIENTES_SQL,
                batch,
                "Pacientes",
                total_inserted,
            )
    except psycopg2.Error as e:
        logger.error(f"Erro ao seed de pacientes: {e}")
        conn.rollback()
    
    return total_inserted


def seed_convenios(
    conn: psycopg2.extensions.connection,
    count: int,
    batch_size: int,
) -> int:
    """Popula tabela de convênios."""
    logger.info(f"Iniciando seed de {count} convênios...")
    
    total_inserted = 0
    batch = []
    
    try:
        for _ in range(count):
            convenio = generate_convenio()
            batch.append(
                (
                    convenio["nome"],
                    convenio["cnpj"],
                    convenio["tipo"],
                    convenio["cobertura"],
                )
            )
            
            if len(batch) >= batch_size:
                total_inserted = flush_insert_batch(
                    conn,
                    INSERT_CONVENIOS_SQL,
                    batch,
                    "Convênios",
                    total_inserted,
                )
                batch = []
        
        # Último batch
        if batch:
            total_inserted = flush_insert_batch(
                conn,
                INSERT_CONVENIOS_SQL,
                batch,
                "Convênios",
                total_inserted,
            )
    except psycopg2.Error as e:
        logger.error(f"Erro ao seed de convênios: {e}")
        conn.rollback()
    
    return total_inserted


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

    def flush_batch() -> int:
        nonlocal batch
        if not batch:
            return 0

        with conn.cursor() as cur:
            inserted_rows = execute_values(
                cur,
                """
                INSERT INTO pacientes_convenios
                (paciente_id, convenio_id, numero_carteira, validade)
                VALUES %s
                ON CONFLICT DO NOTHING
                RETURNING id
                """,
                batch,
                fetch=True,
            )
        conn.commit()
        inserted = len(inserted_rows)
        batch = []
        return inserted
    
    try:
        while total_inserted < count and attempts < max_attempts:
            attempts += 1
            paciente_id = validators.get_random_paciente_id()
            convenio_id = validators.get_random_convenio_id()
            
            if paciente_id and convenio_id:
                batch.append(
                    (
                        paciente_id,
                        convenio_id,
                        f"CARTEIRA-{paciente_id}-{convenio_id}",
                        datetime.now().date(),
                    )
                )
            
            if len(batch) >= batch_size or total_inserted + len(batch) >= count:
                inserted = flush_batch()
                total_inserted += inserted
                logger.info(
                    f"Pacientes_Convênios: +{inserted} (total={total_inserted})"
                )
        
        if batch:
            inserted = flush_batch()
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
    
    total_inserted = 0
    batch = []
    validators = Validators(conn)
    
    try:
        for _ in range(count):
            paciente_id = validators.get_random_paciente_id()
            medico_id = validators.get_random_medico_id()
            
            if paciente_id and medico_id:
                consulta = generate_consulta(paciente_id, medico_id)
                batch.append(
                    (
                        consulta["paciente_id"],
                        consulta["medico_id"],
                        consulta["data"],
                        consulta["motivo"],
                        consulta["status"],
                    )
            )
            
            if len(batch) >= batch_size:
                total_inserted = flush_insert_batch(
                    conn,
                    INSERT_CONSULTAS_SQL,
                    batch,
                    "Consultas",
                    total_inserted,
                )
                batch = []
        
        # Último batch
        if batch:
            total_inserted = flush_insert_batch(
                conn,
                INSERT_CONSULTAS_SQL,
                batch,
                "Consultas",
                total_inserted,
            )
    except psycopg2.Error as e:
        logger.error(f"Erro ao seed de consultas: {e}")
        conn.rollback()
    
    return total_inserted


def seed_exames(
    conn: psycopg2.extensions.connection,
    count: int,
    batch_size: int,
) -> int:
    """Popula tabela de exames."""
    logger.info(f"Iniciando seed de {count} exames...")
    
    total_inserted = 0
    batch = []
    validators = Validators(conn)
    
    try:
        for _ in range(count):
            paciente_id = validators.get_random_paciente_id()
            
            if paciente_id:
                exame = generate_exame(paciente_id)
                batch.append(
                    (
                        exame["paciente_id"],
                        exame["tipo_exame"],
                        exame["data"],
                        exame["resultado"],
                    )
            )
            
            if len(batch) >= batch_size:
                total_inserted = flush_insert_batch(
                    conn,
                    INSERT_EXAMES_SQL,
                    batch,
                    "Exames",
                    total_inserted,
                )
                batch = []
        
        # Último batch
        if batch:
            total_inserted = flush_insert_batch(
                conn,
                INSERT_EXAMES_SQL,
                batch,
                "Exames",
                total_inserted,
            )
    except psycopg2.Error as e:
        logger.error(f"Erro ao seed de exames: {e}")
        conn.rollback()
    
    return total_inserted


def seed_internacoes(
    conn: psycopg2.extensions.connection,
    count: int,
    batch_size: int,
) -> int:
    """Popula tabela de internações."""
    logger.info(f"Iniciando seed de {count} internações...")
    
    total_inserted = 0
    batch = []
    validators = Validators(conn)
    
    try:
        for _ in range(count):
            paciente_id = validators.get_random_paciente_id()
            
            if paciente_id:
                internacao = generate_internacao(paciente_id)
                batch.append(
                    (
                        internacao["paciente_id"],
                        internacao["data_entrada"],
                        internacao["data_saida"],
                        internacao["motivo"],
                        internacao["quarto"],
                    )
            )
            
            if len(batch) >= batch_size:
                total_inserted = flush_insert_batch(
                    conn,
                    INSERT_INTERNACOES_SQL,
                    batch,
                    "Internações",
                    total_inserted,
                )
                batch = []
        
        # Último batch
        if batch:
            total_inserted = flush_insert_batch(
                conn,
                INSERT_INTERNACOES_SQL,
                batch,
                "Internações",
                total_inserted,
            )
    except psycopg2.Error as e:
        logger.error(f"Erro ao seed de internações: {e}")
        conn.rollback()
    
    return total_inserted


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
    
    # Seed em ordem
    seed_medicos(conn, config["seed_medicos"], config["batch_size"])
    seed_pacientes(conn, config["seed_pacientes"], config["batch_size"])
    seed_convenios(conn, config["seed_convenios"], config["batch_size"])
    seed_pacientes_convenios(
        conn,
        config["seed_pacientes_convenios"],
        config["batch_size"],
    )
    seed_consultas(conn, config["seed_consultas"], config["batch_size"])
    seed_exames(conn, config["seed_exames"], config["batch_size"])
    seed_internacoes(
        conn,
        config["seed_internacoes"],
        config["batch_size"],
    )
    
    logger.info("Seed concluído com sucesso!")
    conn.close()


if __name__ == "__main__":
    main()
