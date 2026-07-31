import unittest
from unittest.mock import patch

from scripts import stream


class StreamTests(unittest.TestCase):
    def test_stream_loop_stops_after_configured_cycles(self):
        with (
            patch("scripts.stream.random.choices", return_value=["insert_paciente"]),
            patch("scripts.stream.insert_paciente", return_value=True) as insert_mock,
        ):
            stream.stream_loop(conn=object(), interval=0, max_jitter_ms=0, cycles=3)

        self.assertEqual(insert_mock.call_count, 3)

    def test_stream_loop_does_not_count_failed_operation_as_success(self):
        with (
            self.assertLogs("scripts.stream", level="INFO") as logs,
            patch("scripts.stream.random.choices", return_value=["insert_paciente"]),
            patch("scripts.stream.insert_paciente", side_effect=[False, True]),
        ):
            stream.stream_loop(conn=object(), interval=0, max_jitter_ms=0, cycles=2)

        output = "\n".join(logs.output)
        self.assertIn("SKIP INSERT     paciente | INSERT:    0 | UPDATE:    0", output)
        self.assertIn("OK INSERT     paciente | INSERT:    1 | UPDATE:    0", output)


if __name__ == "__main__":
    unittest.main()
