-- Função para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at := now();
  RETURN NEW;
END; $$ LANGUAGE plpgsql;

-- Tabela: pacientes
CREATE TABLE IF NOT EXISTS pacientes (
  id            BIGSERIAL PRIMARY KEY,
  nome          VARCHAR(150) NOT NULL,
  nascimento    DATE NOT NULL,
  cpf           VARCHAR(20) UNIQUE NOT NULL,
  telefone      VARCHAR(20),
  endereco      VARCHAR(200),
  data_cadastro TIMESTAMP NOT NULL DEFAULT now(),
  created_at    TIMESTAMP NOT NULL DEFAULT now(),
  updated_at    TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TRIGGER pacientes_updated_at
BEFORE UPDATE ON pacientes
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- Tabela: medicos
CREATE TABLE IF NOT EXISTS medicos (
  id            BIGSERIAL PRIMARY KEY,
  nome          VARCHAR(150) NOT NULL,
  crm           VARCHAR(20) UNIQUE NOT NULL,
  especialidade VARCHAR(80) NOT NULL,
  telefone      VARCHAR(20),
  created_at    TIMESTAMP NOT NULL DEFAULT now(),
  updated_at    TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TRIGGER medicos_updated_at
BEFORE UPDATE ON medicos
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- Tabela: convenios
CREATE TABLE IF NOT EXISTS convenios (
  id         BIGSERIAL PRIMARY KEY,
  nome       VARCHAR(120) NOT NULL,
  cnpj       VARCHAR(25) UNIQUE NOT NULL,
  tipo       VARCHAR(40) NOT NULL,
  cobertura  VARCHAR(120),
  created_at TIMESTAMP NOT NULL DEFAULT now(),
  updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TRIGGER convenios_updated_at
BEFORE UPDATE ON convenios
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- Tabela N:N: pacientes_convenios
CREATE TABLE IF NOT EXISTS pacientes_convenios (
  id           BIGSERIAL PRIMARY KEY,
  paciente_id  BIGINT NOT NULL REFERENCES pacientes(id)
               ON UPDATE CASCADE ON DELETE RESTRICT,
  convenio_id  BIGINT NOT NULL REFERENCES convenios(id)
               ON UPDATE CASCADE ON DELETE RESTRICT,
  numero_carteira VARCHAR(40),
  validade     DATE,
  created_at   TIMESTAMP NOT NULL DEFAULT now(),
  updated_at   TIMESTAMP NOT NULL DEFAULT now(),
  UNIQUE (paciente_id, convenio_id)
);

CREATE TRIGGER pacientes_convenios_updated_at
BEFORE UPDATE ON pacientes_convenios
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- Tabela: consultas
CREATE TABLE IF NOT EXISTS consultas (
  id          BIGSERIAL PRIMARY KEY,
  paciente_id BIGINT NOT NULL REFERENCES pacientes(id)
              ON UPDATE CASCADE ON DELETE RESTRICT,
  medico_id   BIGINT NOT NULL REFERENCES medicos(id)
              ON UPDATE CASCADE ON DELETE RESTRICT,
  data        TIMESTAMP NOT NULL,
  motivo      VARCHAR(200) NOT NULL,
  status      VARCHAR(20) NOT NULL CHECK (status IN ('agendada','realizada','cancelada','faltou')),
  created_at  TIMESTAMP NOT NULL DEFAULT now(),
  updated_at  TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TRIGGER consultas_updated_at
BEFORE UPDATE ON consultas
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- Tabela: exames
CREATE TABLE IF NOT EXISTS exames (
  id           BIGSERIAL PRIMARY KEY,
  paciente_id  BIGINT NOT NULL REFERENCES pacientes(id)
               ON UPDATE CASCADE ON DELETE RESTRICT,
  tipo_exame   VARCHAR(100) NOT NULL,
  data         TIMESTAMP NOT NULL,
  resultado    VARCHAR(200),
  created_at   TIMESTAMP NOT NULL DEFAULT now(),
  updated_at   TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TRIGGER exames_updated_at
BEFORE UPDATE ON exames
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- Tabela: internacoes
CREATE TABLE IF NOT EXISTS internacoes (
  id           BIGSERIAL PRIMARY KEY,
  paciente_id  BIGINT NOT NULL REFERENCES pacientes(id)
               ON UPDATE CASCADE ON DELETE RESTRICT,
  data_entrada TIMESTAMP NOT NULL,
  data_saida   TIMESTAMP,
  motivo       VARCHAR(200) NOT NULL,
  quarto       VARCHAR(20),
  created_at   TIMESTAMP NOT NULL DEFAULT now(),
  updated_at   TIMESTAMP NOT NULL DEFAULT now(),
  CHECK (data_saida IS NULL OR data_saida >= data_entrada)
);

CREATE TRIGGER internacoes_updated_at
BEFORE UPDATE ON internacoes
FOR EACH ROW EXECUTE FUNCTION set_updated_at();
