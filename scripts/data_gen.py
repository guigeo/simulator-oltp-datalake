"""
Utilitários de geração de dados usando Faker.
Locale pt_BR, com funções para gerar pacientes, médicos, convênios, etc.
"""

import random
import string
from datetime import datetime, timedelta
from typing import Dict, Any, Set

from faker import Faker

fake = Faker("pt_BR")


def generate_cpf() -> str:
    """Gera um CPF formatado único (XXX.XXX.XXX-XX)."""
    cpf = [random.randint(0, 9) for _ in range(9)]
    
    s = sum((i + 2) * cpf[i] for i in range(8))
    cpf.append((11 - (s % 11)) % 11)
    
    s = sum((i + 1) * cpf[i] for i in range(9))
    cpf.append((11 - (s % 11)) % 11)
    
    return f"{cpf[0]}{cpf[1]}{cpf[2]}.{cpf[3]}{cpf[4]}{cpf[5]}.{cpf[6]}{cpf[7]}{cpf[8]}-{cpf[9]}{cpf[10]}"


def generate_crm() -> str:
    """Gera um CRM único (6 dígitos + UF 2 letras)."""
    num = random.randint(100000, 999999)
    uf = "".join(random.choices(string.ascii_uppercase, k=2))
    return f"{num}{uf}"


def generate_cnpj() -> str:
    """Gera um CNPJ formatado único (XX.XXX.XXX/0001-XX)."""
    cnpj = [random.randint(0, 9) for _ in range(8)]
    cnpj += [0, 0, 0, 1]
    
    s = sum((i % 8 + 2) * cnpj[i] for i in range(12))
    cnpj.append((11 - (s % 11)) % 11)
    
    s = sum((i % 8 + 2) * cnpj[i] for i in range(13))
    cnpj.append((11 - (s % 11)) % 11)
    
    return (
        f"{cnpj[0]}{cnpj[1]}.{cnpj[2]}{cnpj[3]}{cnpj[4]}.{cnpj[5]}{cnpj[6]}{cnpj[7]}/"
        f"{cnpj[8]}{cnpj[9]}{cnpj[10]}{cnpj[11]}-{cnpj[12]}{cnpj[13]}"
    )


def generate_paciente() -> Dict[str, Any]:
    """Gera dados de um paciente."""
    hoje = datetime.now().date()
    nascimento = fake.date_of_birth(minimum_age=18, maximum_age=100)
    
    return {
        "nome": fake.name(),
        "nascimento": nascimento,
        "cpf": generate_cpf(),
        "telefone": fake.phone_number(),
        "endereco": fake.address().replace("\n", " "),
        "data_cadastro": fake.date_between(start_date="-2y", end_date="today"),
    }


def generate_medico() -> Dict[str, Any]:
    """Gera dados de um médico."""
    especialidades = [
        "Clínica Geral",
        "Cardiologia",
        "Pneumologia",
        "Gastroenterologia",
        "Neurologia",
        "Ortopedia",
        "Dermatologia",
        "Oftalmologia",
        "Otorrinolaringologia",
        "Psiquiatria",
    ]
    
    return {
        "nome": fake.name(),
        "crm": generate_crm(),
        "especialidade": random.choice(especialidades),
        "telefone": fake.phone_number(),
    }


def generate_convenio() -> Dict[str, Any]:
    """Gera dados de um convênio."""
    tipos = ["publico", "privado", "empresarial"]
    coberturas = [
        "integral",
        "ambulatorial e hospitalar",
        "ambulatorial",
        "especializado",
    ]
    
    return {
        "nome": fake.company(),
        "cnpj": generate_cnpj(),
        "tipo": random.choice(tipos),
        "cobertura": random.choice(coberturas),
    }


def generate_consulta(
    paciente_id: int,
    medico_id: int,
    min_date: datetime = None,
) -> Dict[str, Any]:
    """Gera dados de uma consulta."""
    if min_date is None:
        min_date = datetime.now() - timedelta(days=730)
    
    motivos = [
        "Consulta de rotina",
        "Acompanhamento",
        "Queixa principal",
        "Revisão de exames",
        "Prescrição de medicamentos",
        "Avaliação de sintomas",
    ]
    
    status_choices = ["agendada", "realizada", "cancelada", "faltou"]
    status_weights = [0.55, 0.35, 0.05, 0.05]
    
    data = fake.date_time_between(
        start_date=min_date,
        end_date="+2y",
    )
    
    return {
        "paciente_id": paciente_id,
        "medico_id": medico_id,
        "data": data,
        "motivo": random.choice(motivos),
        "status": random.choices(status_choices, weights=status_weights)[0],
    }


def generate_exame(
    paciente_id: int,
    min_date: datetime = None,
) -> Dict[str, Any]:
    """Gera dados de um exame."""
    if min_date is None:
        min_date = datetime.now() - timedelta(days=730)
    
    tipos = [
        "Hemograma",
        "Raio-X",
        "Tomografia",
        "Ultrassom",
        "PCR",
        "ECG",
        "Eletrocardiograma",
        "Ressonância Magnética",
        "Biópsia",
        "Endoscopia",
    ]
    
    resultados = [
        "Normal",
        "Alterado",
        "Pendente de análise",
        "Requer acompanhamento",
        "Sem alterações",
    ]
    
    data = fake.date_time_between(
        start_date=min_date,
        end_date="+2y",
    )
    
    return {
        "paciente_id": paciente_id,
        "tipo_exame": random.choice(tipos),
        "data": data,
        "resultado": random.choice(resultados),
    }


def generate_internacao(
    paciente_id: int,
    min_date: datetime = None,
) -> Dict[str, Any]:
    """Gera dados de uma internação."""
    if min_date is None:
        min_date = datetime.now() - timedelta(days=730)
    
    motivos = [
        "Cirurgia",
        "Tratamento de infecção",
        "Observação",
        "Reabilitação",
        "Cuidados paliativos",
        "Avaliação diagnóstica",
    ]
    
    data_entrada = fake.date_time_between(
        start_date=min_date,
        end_date="+2y",
    )
    
    # 70% têm alta, 30% ainda estão internados
    data_saida = None
    if random.random() < 0.7:
        data_saida = data_entrada + timedelta(days=random.randint(1, 10))
    
    quartos = [
        "101",
        "102",
        "103",
        "201",
        "202",
        "203",
        "301",
        "302",
        "303",
    ]
    
    return {
        "paciente_id": paciente_id,
        "data_entrada": data_entrada,
        "data_saida": data_saida,
        "motivo": random.choice(motivos),
        "quarto": random.choice(quartos),
    }
