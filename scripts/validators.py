"""
Validadores de integridade, domínios e FKs com cache LRU.
"""

from functools import lru_cache
from typing import Optional
import psycopg2
from psycopg2 import sql


class Validators:
    """Validador com cache LRU para FKs."""

    def __init__(self, conn: psycopg2.extensions.connection):
        """Inicializa validador com conexão ao DB."""
        self.conn = conn

    @lru_cache(maxsize=512)
    def check_paciente_exists(self, paciente_id: int) -> bool:
        """Verifica se paciente existe (com cache)."""
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM pacientes WHERE id = %s LIMIT 1",
                (paciente_id,),
            )
            return cur.fetchone() is not None

    @lru_cache(maxsize=512)
    def check_medico_exists(self, medico_id: int) -> bool:
        """Verifica se médico existe (com cache)."""
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM medicos WHERE id = %s LIMIT 1",
                (medico_id,),
            )
            return cur.fetchone() is not None

    @lru_cache(maxsize=512)
    def check_convenio_exists(self, convenio_id: int) -> bool:
        """Verifica se convênio existe (com cache)."""
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM convenios WHERE id = %s LIMIT 1",
                (convenio_id,),
            )
            return cur.fetchone() is not None

    def get_random_paciente_id(self) -> Optional[int]:
        """Retorna um ID aleatório de paciente."""
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM pacientes ORDER BY RANDOM() LIMIT 1"
            )
            row = cur.fetchone()
            return row[0] if row else None

    def get_random_medico_id(self) -> Optional[int]:
        """Retorna um ID aleatório de médico."""
        with self.conn.cursor() as cur:
            cur.execute("SELECT id FROM medicos ORDER BY RANDOM() LIMIT 1")
            row = cur.fetchone()
            return row[0] if row else None

    def get_random_convenio_id(self) -> Optional[int]:
        """Retorna um ID aleatório de convênio."""
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM convenios ORDER BY RANDOM() LIMIT 1"
            )
            row = cur.fetchone()
            return row[0] if row else None

    def get_paciente_count(self) -> int:
        """Retorna contagem de pacientes."""
        with self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM pacientes")
            return cur.fetchone()[0]

    def get_medico_count(self) -> int:
        """Retorna contagem de médicos."""
        with self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM medicos")
            return cur.fetchone()[0]

    def get_convenio_count(self) -> int:
        """Retorna contagem de convênios."""
        with self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM convenios")
            return cur.fetchone()[0]

    def is_valid_status_consulta(self, status: str) -> bool:
        """Valida status de consulta."""
        valid = {"agendada", "realizada", "cancelada", "faltou"}
        return status in valid

    def is_valid_tipo_convenio(self, tipo: str) -> bool:
        """Valida tipo de convênio."""
        valid = {"publico", "privado", "empresarial"}
        return tipo in valid

    def clear_cache(self) -> None:
        """Limpa cache LRU."""
        self.check_paciente_exists.cache_clear()
        self.check_medico_exists.cache_clear()
        self.check_convenio_exists.cache_clear()
