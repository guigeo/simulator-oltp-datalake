"""
Inicialização do banco de dados: conexão, schema, índices e seed lookups.
"""

import logging
import os
from pathlib import Path
from typing import Optional

import psycopg2
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def load_env() -> dict:
    """Carrega variáveis de ambiente."""
    load_dotenv(Path(__file__).parent.parent / "config" / ".env")
    return {
        "host": os.getenv("PG_HOST", "localhost"),
        "port": int(os.getenv("PG_PORT", 5432)),
        "user": os.getenv("PG_USER", "postgres"),
        "password": os.getenv("PG_PASSWORD", "postgres"),
        "database": os.getenv("PG_DATABASE", "hospital_oltp"),
    }


def create_connection(env_vars: Optional[dict] = None) -> psycopg2.extensions.connection:
    """Cria conexão com o PostgreSQL."""
    if env_vars is None:
        env_vars = load_env()
    
    try:
        conn = psycopg2.connect(
            host=env_vars["host"],
            port=env_vars["port"],
            user=env_vars["user"],
            password=env_vars["password"],
            database=env_vars["database"],
            connect_timeout=10,
            application_name="oltp-simulator",
        )
        conn.autocommit = False
        conn.isolation_level = psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED
        logger.info("Conexão com PostgreSQL estabelecida com sucesso.")
        return conn
    except psycopg2.Error as e:
        logger.error(f"Erro ao conectar ao PostgreSQL: {e}")
        raise


def test_connection(conn: psycopg2.extensions.connection) -> bool:
    """Testa conexão com SELECT 1."""
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
        logger.info("Conexão validada com sucesso.")
        return True
    except psycopg2.Error as e:
        logger.error(f"Erro ao testar conexão: {e}")
        return False


def execute_sql_file(
    conn: psycopg2.extensions.connection,
    file_path: str,
) -> bool:
    """Executa um arquivo SQL."""
    try:
        with open(file_path, "r") as f:
            sql_content = f.read()
        
        with conn.cursor() as cur:
            cur.execute(sql_content)
        
        conn.commit()
        logger.info(f"Arquivo SQL executado com sucesso: {file_path}")
        return True
    except psycopg2.Error as e:
        logger.error(f"Erro ao executar {file_path}: {e}")
        conn.rollback()
        return False
    except FileNotFoundError:
        logger.error(f"Arquivo não encontrado: {file_path}")
        return False


def init_db(
    conn: psycopg2.extensions.connection,
    drop_first: bool = False,
) -> bool:
    """Inicializa o banco: drop, schema, índices, seed lookups."""
    sql_dir = Path(__file__).parent.parent / "sql"
    
    # 1) Drop (opcional)
    if drop_first:
        logger.info("Executando drop de todas as tabelas...")
        if not execute_sql_file(conn, str(sql_dir / "99_drop_all.sql")):
            return False
    
    # 2) Schema
    logger.info("Criando schema...")
    if not execute_sql_file(conn, str(sql_dir / "01_schema.sql")):
        return False
    
    # 3) Índices
    logger.info("Criando índices...")
    if not execute_sql_file(conn, str(sql_dir / "02_indexes.sql")):
        return False
    
    # 4) Seed lookups
    logger.info("Carregando dados de lookup...")
    if not execute_sql_file(conn, str(sql_dir / "03_seed-lookups.sql")):
        return False
    
    logger.info("Banco de dados inicializado com sucesso.")
    return True


def get_table_counts(conn: psycopg2.extensions.connection) -> dict:
    """Retorna contagem de registros por tabela."""
    tables = [
        "pacientes",
        "medicos",
        "convenios",
        "pacientes_convenios",
        "consultas",
        "exames",
        "internacoes",
    ]
    
    counts = {}
    try:
        with conn.cursor() as cur:
            for table in tables:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                counts[table] = cur.fetchone()[0]
    except psycopg2.Error as e:
        logger.error(f"Erro ao contar registros: {e}")
    
    return counts
