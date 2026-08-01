import unittest
from unittest.mock import MagicMock

from app.dashboard_data import fetch_one, fetch_rows


class DashboardDataTests(unittest.TestCase):
    def test_fetch_rows_returns_dicts_from_cursor_description(self):
        cursor = MagicMock()
        cursor.description = [("id",), ("nome",)]
        cursor.fetchall.return_value = [(1, "Ana"), (2, "Bruno")]
        conn = MagicMock()
        conn.cursor.return_value.__enter__.return_value = cursor

        rows = fetch_rows(conn, "SELECT id, nome FROM pacientes WHERE id > %s", (0,))

        cursor.execute.assert_called_once_with(
            "SELECT id, nome FROM pacientes WHERE id > %s",
            (0,),
        )
        self.assertEqual(
            rows,
            [
                {"id": 1, "nome": "Ana"},
                {"id": 2, "nome": "Bruno"},
            ],
        )

    def test_fetch_one_returns_first_row(self):
        cursor = MagicMock()
        cursor.description = [("total",)]
        cursor.fetchall.return_value = [(3,)]
        conn = MagicMock()
        conn.cursor.return_value.__enter__.return_value = cursor

        row = fetch_one(conn, "SELECT COUNT(*) AS total FROM pacientes")

        self.assertEqual(row, {"total": 3})

    def test_fetch_one_returns_empty_dict_without_rows(self):
        cursor = MagicMock()
        cursor.description = [("total",)]
        cursor.fetchall.return_value = []
        conn = MagicMock()
        conn.cursor.return_value.__enter__.return_value = cursor

        row = fetch_one(conn, "SELECT COUNT(*) AS total FROM pacientes")

        self.assertEqual(row, {})


if __name__ == "__main__":
    unittest.main()
