import unittest

import psycopg2

from scripts.db_init import create_connection, get_table_counts, load_env


EXPECTED_TABLES = {
    "pacientes",
    "medicos",
    "convenios",
    "pacientes_convenios",
    "consultas",
    "exames",
    "internacoes",
}


class PostgresIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.env = load_env()
        try:
            cls.conn = create_connection(cls.env)
        except psycopg2.Error as exc:
            raise unittest.SkipTest(f"PostgreSQL indisponivel: {exc}") from exc

    @classmethod
    def tearDownClass(cls):
        conn = getattr(cls, "conn", None)
        if conn is not None:
            conn.close()

    def test_connection_uses_project_database(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT current_database(), current_user")
            database, user = cur.fetchone()

        self.assertEqual(database, self.env["database"])
        self.assertEqual(user, self.env["user"])

    def test_expected_tables_exist(self):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                """
            )
            tables = {row[0] for row in cur.fetchall()}

        self.assertTrue(EXPECTED_TABLES.issubset(tables))

    def test_table_counts_are_available(self):
        counts = get_table_counts(self.conn)

        self.assertEqual(set(counts), EXPECTED_TABLES)
        for count in counts.values():
            self.assertGreaterEqual(count, 0)

    def test_logical_replication_is_enabled(self):
        with self.conn.cursor() as cur:
            cur.execute("SHOW wal_level")
            wal_level = cur.fetchone()[0]
            cur.execute("SHOW max_replication_slots")
            max_replication_slots = int(cur.fetchone()[0])

        self.assertEqual(wal_level, "logical")
        self.assertGreater(max_replication_slots, 0)


if __name__ == "__main__":
    unittest.main()
