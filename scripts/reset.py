"""
Reset: drop + recreate + seed completo.
"""

import logging

from scripts.db_init import load_env, create_connection, test_connection, init_db, get_table_counts
from scripts.seed import main as seed_main

logger = logging.getLogger(__name__)


def main():
    """Executa reset completo."""
    env_vars = load_env()
    
    conn = create_connection(env_vars)
    if not test_connection(conn):
        logger.error("Falha ao testar conexão com o banco.")
        conn.close()
        return
    
    logger.info("Iniciando reset completo...")
    
    # 1) Drop e recreate
    if not init_db(conn, drop_first=True):
        logger.error("Falha ao inicializar banco.")
        conn.close()
        return
    
    conn.close()
    
    # 2) Seed
    seed_main()
    
    # 3) Exibe resumo
    conn = create_connection(env_vars)
    counts = get_table_counts(conn)
    
    logger.info("=== Resumo Final ===")
    for table, count in counts.items():
        logger.info(f"{table}: {count} registros")
    
    conn.close()
    logger.info("Reset concluído com sucesso!")


if __name__ == "__main__":
    main()
