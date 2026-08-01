import unittest
from unittest.mock import MagicMock, Mock, patch

import psycopg2

from scripts.seed import (
    flush_conflict_aware_batch,
    flush_insert_batch,
    log_seed_summary,
    run_seed,
    seed_insert_rows,
)


class SeedTests(unittest.TestCase):
    def test_flush_insert_batch_commits_and_returns_total(self):
        cursor = Mock()
        conn = MagicMock()
        conn.cursor.return_value.__enter__.return_value = cursor
        batch = [("a",), ("b",)]

        with patch("scripts.seed.execute_values") as execute_values:
            total = flush_insert_batch(
                conn,
                "INSERT INTO table VALUES %s",
                batch,
                "Rows",
                3,
            )

        execute_values.assert_called_once_with(
            cursor,
            "INSERT INTO table VALUES %s",
            batch,
        )
        conn.commit.assert_called_once_with()
        self.assertEqual(total, 5)

    def test_flush_insert_batch_skips_empty_batch(self):
        conn = Mock()

        total = flush_insert_batch(
            conn,
            "INSERT INTO table VALUES %s",
            [],
            "Rows",
            3,
        )

        conn.cursor.assert_not_called()
        conn.commit.assert_not_called()
        self.assertEqual(total, 3)

    def test_seed_insert_rows_flushes_full_and_final_batches(self):
        conn = MagicMock()
        rows = iter([("a",), ("b",), ("c",)])

        with patch("scripts.seed.flush_insert_batch", side_effect=[2, 3]) as flush:
            total = seed_insert_rows(
                conn,
                count=3,
                batch_size=2,
                sql="INSERT INTO table VALUES %s",
                label="Rows",
                error_label="rows",
                row_factory=lambda: next(rows),
            )

        self.assertEqual(total, 3)
        self.assertEqual(flush.call_count, 2)
        self.assertEqual(flush.call_args_list[0].args[2], [("a",), ("b",)])
        self.assertEqual(flush.call_args_list[1].args[2], [("c",)])

    def test_seed_insert_rows_ignores_empty_rows(self):
        conn = MagicMock()
        rows = iter([None, ("a",), None])

        with patch("scripts.seed.flush_insert_batch", side_effect=[1]) as flush:
            total = seed_insert_rows(
                conn,
                count=3,
                batch_size=10,
                sql="INSERT INTO table VALUES %s",
                label="Rows",
                error_label="rows",
                row_factory=lambda: next(rows),
            )

        self.assertEqual(total, 1)
        flush.assert_called_once()
        self.assertEqual(flush.call_args.args[2], [("a",)])

    def test_seed_insert_rows_rolls_back_and_returns_partial_total_on_error(self):
        conn = MagicMock()
        rows = iter([("a",), ("b",)])

        with (
            self.assertLogs("scripts.seed", level="ERROR"),
            patch(
                "scripts.seed.flush_insert_batch",
                side_effect=[1, psycopg2.Error("boom")],
            ),
        ):
            total = seed_insert_rows(
                conn,
                count=2,
                batch_size=1,
                sql="INSERT INTO table VALUES %s",
                label="Rows",
                error_label="rows",
                row_factory=lambda: next(rows),
            )

        self.assertEqual(total, 1)
        conn.rollback.assert_called_once_with()

    def test_flush_conflict_aware_batch_returns_inserted_rows(self):
        cursor = Mock()
        conn = MagicMock()
        conn.cursor.return_value.__enter__.return_value = cursor
        batch = [("a",), ("b",)]

        with patch("scripts.seed.execute_values", return_value=[(1,)]) as execute_values:
            inserted = flush_conflict_aware_batch(
                conn,
                "INSERT INTO table VALUES %s RETURNING id",
                batch,
            )

        execute_values.assert_called_once_with(
            cursor,
            "INSERT INTO table VALUES %s RETURNING id",
            batch,
            fetch=True,
        )
        conn.commit.assert_called_once_with()
        self.assertEqual(inserted, 1)

    def test_flush_conflict_aware_batch_skips_empty_batch(self):
        conn = Mock()

        inserted = flush_conflict_aware_batch(
            conn,
            "INSERT INTO table VALUES %s RETURNING id",
            [],
        )

        conn.cursor.assert_not_called()
        conn.commit.assert_not_called()
        self.assertEqual(inserted, 0)

    def test_run_seed_returns_summary_in_insert_order(self):
        conn = Mock()
        config = {
            "seed_medicos": 1,
            "seed_pacientes": 2,
            "seed_convenios": 3,
            "seed_pacientes_convenios": 4,
            "seed_consultas": 5,
            "seed_exames": 6,
            "seed_internacoes": 7,
            "batch_size": 8,
        }

        patches = [
            patch("scripts.seed.seed_medicos", return_value=10),
            patch("scripts.seed.seed_pacientes", return_value=20),
            patch("scripts.seed.seed_convenios", return_value=30),
            patch("scripts.seed.seed_pacientes_convenios", return_value=40),
            patch("scripts.seed.seed_consultas", return_value=50),
            patch("scripts.seed.seed_exames", return_value=60),
            patch("scripts.seed.seed_internacoes", return_value=70),
        ]

        with (
            patches[0] as medicos,
            patches[1] as pacientes,
            patches[2] as convenios,
            patches[3] as pacientes_convenios,
            patches[4] as consultas,
            patches[5] as exames,
            patches[6] as internacoes,
        ):
            summary = run_seed(conn, config)

        self.assertEqual(
            summary,
            {
                "medicos": 10,
                "pacientes": 20,
                "convenios": 30,
                "pacientes_convenios": 40,
                "consultas": 50,
                "exames": 60,
                "internacoes": 70,
            },
        )
        medicos.assert_called_once_with(conn, 1, 8)
        pacientes.assert_called_once_with(conn, 2, 8)
        convenios.assert_called_once_with(conn, 3, 8)
        pacientes_convenios.assert_called_once_with(conn, 4, 8)
        consultas.assert_called_once_with(conn, 5, 8)
        exames.assert_called_once_with(conn, 6, 8)
        internacoes.assert_called_once_with(conn, 7, 8)

    def test_log_seed_summary_logs_total(self):
        summary = {"medicos": 2, "pacientes": 3}

        with self.assertLogs("scripts.seed", level="INFO") as logs:
            log_seed_summary(summary)

        output = "\n".join(logs.output)
        self.assertIn("Resumo do seed", output)
        self.assertIn("medicos: 2", output)
        self.assertIn("pacientes: 3", output)
        self.assertIn("Total inserido no seed: 5", output)


if __name__ == "__main__":
    unittest.main()
