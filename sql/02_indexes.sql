-- Índices úteis para consultas e CDC (chaves naturais e FK targets)
CREATE INDEX IF NOT EXISTS idx_pacientes_cpf ON pacientes (cpf);
CREATE INDEX IF NOT EXISTS idx_medicos_crm ON medicos (crm);
CREATE INDEX IF NOT EXISTS idx_consultas_paciente ON consultas (paciente_id);
CREATE INDEX IF NOT EXISTS idx_consultas_medico ON consultas (medico_id);
CREATE INDEX IF NOT EXISTS idx_consultas_data ON consultas (data);
CREATE INDEX IF NOT EXISTS idx_exames_paciente ON exames (paciente_id);
CREATE INDEX IF NOT EXISTS idx_exames_data ON exames (data);
CREATE INDEX IF NOT EXISTS idx_internacoes_paciente ON internacoes (paciente_id);
CREATE INDEX IF NOT EXISTS idx_internacoes_datas ON internacoes (data_entrada, data_saida);
