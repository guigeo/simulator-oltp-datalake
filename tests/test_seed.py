import unittest
from unittest.mock import MagicMock, Mock, patch

import psycopg2

from scripts.seed import flush_insert_batch, seed_insert_rows


class SeedTests(unittest.TestCase):
    def test_flush_insert_batch_commits_and_returns_total(self):
        cursor = Mock()
        conn = MagicMock()
        conn.cursor.return_value.__enter__.return_value = cursor
        batch = [("a",), ("b",)]

        with patch("scripts.seed.execute_values") as execute_values:
            total = flush_insert_batch(conn, "INSERT INTO table VALUES %s", batch, "Rows", 3)

        execute_values.assert_called_once_with(
            cursor,
            "INSERT INTO table VALUES %s",
            batch,
        )
        conn.commit.assert_called_once_with()
        self.assertEqual(total, 5)

    def test_flush_insert_batch_skips_empty_batch(self):
        conn = Mock()

        total = flush_insert_batch(conn, "INSERT INTO table VALUES %s", [], "Rows", 3)

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


if __name__ == "__main__":
    unittest.main()
