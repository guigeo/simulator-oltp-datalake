import os
import unittest
from unittest.mock import patch

from scripts.db_init import load_env
from scripts.seed import load_config as load_seed_config
from scripts.stream import load_config as load_stream_config


class ConfigTests(unittest.TestCase):
    def test_load_env_prefers_exported_variables(self):
        env = {
            "PG_HOST": "db.local",
            "PG_PORT": "5544",
            "PG_USER": "tester",
            "PG_PASSWORD": "secret",
            "PG_DATABASE": "hospital_test",
        }

        with patch.dict(os.environ, env, clear=False):
            loaded = load_env()

        self.assertEqual(
            loaded,
            {
                "host": "db.local",
                "port": 5544,
                "user": "tester",
                "password": "secret",
                "database": "hospital_test",
            },
        )

    def test_stream_config_prefers_exported_variables(self):
        env = {
            "STREAM_INTERVAL_SECONDS": "7",
            "BATCH_SIZE": "11",
            "MAX_JITTER_MS": "23",
        }

        with patch.dict(os.environ, env, clear=False):
            config = load_stream_config()

        self.assertEqual(config["interval"], 7)
        self.assertEqual(config["batch_size"], 11)
        self.assertEqual(config["max_jitter_ms"], 23)

    def test_seed_config_prefers_exported_variables(self):
        env = {
            "SEED_PACIENTES": "3",
            "SEED_MEDICOS": "4",
            "SEED_CONVENIOS": "5",
            "SEED_CONSULTAS": "6",
            "SEED_EXAMES": "7",
            "SEED_INTERNACOES": "8",
            "SEED_PACIENTES_CONVENIOS": "9",
            "BATCH_SIZE": "2",
        }

        with patch.dict(os.environ, env, clear=False):
            config = load_seed_config()

        self.assertEqual(config["seed_pacientes"], 3)
        self.assertEqual(config["seed_medicos"], 4)
        self.assertEqual(config["seed_convenios"], 5)
        self.assertEqual(config["seed_consultas"], 6)
        self.assertEqual(config["seed_exames"], 7)
        self.assertEqual(config["seed_internacoes"], 8)
        self.assertEqual(config["seed_pacientes_convenios"], 9)
        self.assertEqual(config["batch_size"], 2)


if __name__ == "__main__":
    unittest.main()
