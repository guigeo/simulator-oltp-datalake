import unittest
from unittest.mock import MagicMock, Mock, patch

from scripts.seed import flush_insert_batch


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


if __name__ == "__main__":
    unittest.main()
