-- Exemplos de convênios-base (serão ampliados pelo seed.py)
INSERT INTO convenios (nome, cnpj, tipo, cobertura)
VALUES
  ('SUS', '00.000.000/0001-00', 'publico', 'integral'),
  ('SaudePlus', '11.111.111/0001-11', 'privado', 'ambulatorial e hospitalar')
ON CONFLICT DO NOTHING;
