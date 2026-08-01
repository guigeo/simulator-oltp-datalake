import unittest
from unittest.mock import MagicMock

from app.dashboard_data import fetch_one, fetch_rows, get_operational_alerts


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

    def test_get_operational_alerts_returns_exceeded_rules(self):
        snapshot = {
            "kpis": {
                "exames_pendentes": 12,
                "consultas_agendadas": 3,
                "internacoes_ativas": 8,
            },
            "pacientes_sem_convenio": [{"id": 1}],
            "internacoes_longas": [{"id": 2}, {"id": 3}],
        }

        alerts = get_operational_alerts(
            snapshot,
            thresholds={
                "exames_pendentes": 10,
                "consultas_agendadas": 10,
                "internacoes_ativas": 10,
                "pacientes_sem_convenio": 0,
                "internacoes_longas": 0,
            },
        )

        self.assertEqual(
            [alert["codigo"] for alert in alerts],
            [
                "exames_pendentes",
                "pacientes_sem_convenio",
                "internacoes_longas",
            ],
        )

    def test_get_operational_alerts_returns_empty_list_when_within_limits(self):
        snapshot = {
            "kpis": {
                "exames_pendentes": 1,
                "consultas_agendadas": 2,
                "internacoes_ativas": 3,
            },
            "pacientes_sem_convenio": [],
            "internacoes_longas": [],
        }

        alerts = get_operational_alerts(
            snapshot,
            thresholds={
                "exames_pendentes": 10,
                "consultas_agendadas": 10,
                "internacoes_ativas": 10,
                "pacientes_sem_convenio": 0,
                "internacoes_longas": 0,
            },
        )

        self.assertEqual(alerts, [])


if __name__ == "__main__":
    unittest.main()
