"""
CLI com Typer para gerenciar o simulador OLTP.
"""

import logging
from pathlib import Path
from typing import Optional

import typer
from dotenv import load_dotenv

from scripts.db_init import (
    load_env,
    create_connection,
    test_connection,
    init_db,
    get_table_counts,
)
from scripts.seed import main as seed_main
from scripts.stream import main as stream_main
from scripts.reset import main as reset_main

app = typer.Typer(help="Simulador OLTP Hospitalar para testes de CDC")

# Configurar logging
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s [%(funcName)s] - %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "app.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


@app.command()
def init_db_cmd():
    """Inicializa o banco de dados (schema, índices, lookups)."""
    logger.info("Inicializando banco de dados...")
    
    load_dotenv()
    env_vars = load_env()
    
    conn = create_connection(env_vars)
    if not test_connection(conn):
        logger.error("Falha ao testar conexão com o banco.")
        conn.close()
        raise typer.Exit(code=1)
    
    if not init_db(conn, drop_first=False):
        logger.error("Falha ao inicializar banco.")
        conn.close()
        raise typer.Exit(code=1)
    
    conn.close()
    typer.echo("✓ Banco inicializado com sucesso!")


@app.command()
def seed(
    volume: Optional[int] = typer.Option(
        None,
        help="Multiplicador de volume (1x = valores padrão do .env)",
    ),
):
    """Popula o banco com volume inicial de dados."""
    logger.info("Iniciando seed de dados...")
    
    load_dotenv()
    
    if volume and volume > 1:
        logger.info(f"Usando multiplicador de volume: {volume}x")
        import os
        for key in [
            "SEED_PACIENTES",
            "SEED_MEDICOS",
            "SEED_CONVENIOS",
            "SEED_CONSULTAS",
            "SEED_EXAMES",
            "SEED_INTERNACOES",
            "SEED_PACIENTES_CONVENIOS",
        ]:
            if key in os.environ:
                os.environ[key] = str(int(os.getenv(key, 0)) * volume)
    
    try:
        seed_main()
        typer.echo("✓ Seed concluído com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao executar seed: {e}")
        raise typer.Exit(code=1)


@app.command()
def stream(interval: int = 2, batch_size: int = 50):
    """Inicia inserção contínua e realista de eventos."""
    logger.info(f"Iniciando stream (interval={interval}s, batch={batch_size})")
    
    load_dotenv()
    
    try:
        stream_main(interval=interval, batch_size=batch_size)
        typer.echo("✓ Stream encerrado com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao executar stream: {e}")
        raise typer.Exit(code=1)


@app.command()
def reset():
    """Reset total: drop + recreate + seed."""
    logger.info("Executando reset total...")
    
    load_dotenv()
    
    try:
        reset_main()
        typer.echo("✓ Reset concluído com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao executar reset: {e}")
        raise typer.Exit(code=1)


@app.command()
def counts():
    """Exibe contagem de registros por tabela."""
    logger.info("Buscando contagens...")
    
    load_dotenv()
    env_vars = load_env()
    
    conn = create_connection(env_vars)
    if not test_connection(conn):
        logger.error("Falha ao testar conexão com o banco.")
        conn.close()
        raise typer.Exit(code=1)
    
    counts_dict = get_table_counts(conn)
    conn.close()
    
    if not counts_dict:
        logger.error("Falha ao obter contagens.")
        raise typer.Exit(code=1)
    
    typer.echo("\n=== Contagem de Registros ===")
    total = 0
    for table, count in counts_dict.items():
        typer.echo(f"{table:.<30} {count:>10,}")
        total += count
    
    typer.echo("=" * 45)
    typer.echo(f"{'TOTAL':.<30} {total:>10,}")


if __name__ == "__main__":
    app()
