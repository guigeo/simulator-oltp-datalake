import unittest
from datetime import datetime

from scripts.data_gen import (
    generate_cnpj,
    generate_consulta,
    generate_cpf,
    generate_crm,
    generate_exame,
    generate_internacao,
    generate_paciente,
)


class DataGenTests(unittest.TestCase):
    def test_document_formats(self):
        for _ in range(100):
            self.assertRegex(generate_cpf(), r"^\d{3}\.\d{3}\.\d{3}-\d{2}$")
            self.assertRegex(generate_cnpj(), r"^\d{2}\.\d{3}\.\d{3}/0001-\d{2}$")
            self.assertRegex(generate_crm(), r"^\d{6}[A-Z]{2}$")

    def test_paciente_shape(self):
        paciente = generate_paciente()

        self.assertTrue(paciente["nome"])
        self.assertIn("cpf", paciente)
        self.assertNotIn("\n", paciente["endereco"])

    def test_consulta_shape(self):
        consulta = generate_consulta(paciente_id=1, medico_id=2)

        self.assertEqual(consulta["paciente_id"], 1)
        self.assertEqual(consulta["medico_id"], 2)
        self.assertIsInstance(consulta["data"], datetime)
        self.assertIn(
            consulta["status"],
            {"agendada", "realizada", "cancelada", "faltou"},
        )

    def test_exame_shape(self):
        exame = generate_exame(paciente_id=1)

        self.assertEqual(exame["paciente_id"], 1)
        self.assertTrue(exame["tipo_exame"])
        self.assertIsInstance(exame["data"], datetime)

    def test_internacao_saida_never_before_entrada(self):
        for _ in range(100):
            internacao = generate_internacao(paciente_id=1)
            data_saida = internacao["data_saida"]

            if data_saida is not None:
                self.assertGreaterEqual(data_saida, internacao["data_entrada"])


if __name__ == "__main__":
    unittest.main()
