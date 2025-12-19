CREATE OR REFRESH STREAMING LIVE TABLE simulador_oltp_hospital.bronze.consultas
COMMENT "Bronze — eventos CDC de consultas médicas a partir do raw em JSON no S3"
TBLPROPERTIES ("quality" = "bronze")
AS
SELECT
  parsed.after.id            AS id,
  parsed.after.paciente_id   AS paciente_id,
  parsed.after.medico_id     AS medico_id,
  parsed.after.data          AS data_consulta,
  parsed.after.motivo        AS motivo,
  parsed.after.status        AS status,
  parsed.after.created_at    AS created_at,
  parsed.after.updated_at    AS updated_at,

  parsed.op                  AS op,
  parsed.ts_ms               AS cdc_ts,

  CAST(parsed.op = 'd' AS STRING) AS is_deleted
FROM (
  SELECT
    from_json(
      payload,
      'STRUCT<
        before: STRUCT<id: STRING>,
        after: STRUCT<
          id: STRING,
          paciente_id: STRING,
          medico_id: STRING,
          data: STRING,
          motivo: STRING,
          status: STRING,
          created_at: STRING,
          updated_at: STRING
        >,
        op: STRING,
        ts_ms: STRING
      >'
    ) AS parsed
  FROM cloud_files(
    "${input_path_consultas}",
    "json"
  )
);

CREATE OR REFRESH STREAMING LIVE TABLE simulador_oltp_hospital.bronze.pacientes
COMMENT "Bronze — eventos CDC de pacientes a partir do raw em JSON no S3"
TBLPROPERTIES ("quality" = "bronze")
AS
SELECT
  parsed.after.id                AS id,
  parsed.after.nome              AS nome,
  parsed.after.nascimento        AS nascimento,
  parsed.after.cpf               AS cpf,
  parsed.after.telefone          AS telefone,
  parsed.after.endereco          AS endereco,
  parsed.after.data_cadastro     AS data_cadastro,
  parsed.after.created_at        AS created_at,
  parsed.after.updated_at        AS updated_at,

  parsed.op                      AS op,
  parsed.ts_ms                   AS cdc_ts,

  CAST(parsed.op = 'd' AS STRING) AS is_deleted
FROM (
  SELECT
    from_json(
      payload,
      'STRUCT<
        before: STRUCT<id: STRING>,
        after: STRUCT<
          id: STRING,
          nome: STRING,
          nascimento: STRING,
          cpf: STRING,
          telefone: STRING,
          endereco: STRING,
          data_cadastro: STRING,
          created_at: STRING,
          updated_at: STRING
        >,
        op: STRING,
        ts_ms: STRING
      >'
    ) AS parsed
  FROM cloud_files(
    "${input_path_pacientes}",
    "json"
  )
);

CREATE OR REFRESH STREAMING LIVE TABLE simulador_oltp_hospital.bronze.medicos
COMMENT "Bronze — eventos CDC de médicos a partir do raw em JSON no S3"
TBLPROPERTIES ("quality" = "bronze")
AS
SELECT
  parsed.after.id               AS id,
  parsed.after.nome             AS nome,
  parsed.after.crm              AS crm,
  parsed.after.especialidade    AS especialidade,
  parsed.after.telefone         AS telefone,
  parsed.after.created_at       AS created_at,
  parsed.after.updated_at       AS updated_at,

  parsed.op                     AS op,
  parsed.ts_ms                  AS cdc_ts,

  CAST(parsed.op = 'd' AS STRING) AS is_deleted
FROM (
  SELECT
    from_json(
      payload,
      'STRUCT<
        before: STRUCT<id: STRING>,
        after: STRUCT<
          id: STRING,
          nome: STRING,
          crm: STRING,
          especialidade: STRING,
          telefone: STRING,
          created_at: STRING,
          updated_at: STRING
        >,
        op: STRING,
        ts_ms: STRING
      >'
    ) AS parsed
  FROM cloud_files(
    "${input_path_medicos}",
    "json"
  )
);

CREATE OR REFRESH STREAMING LIVE TABLE simulador_oltp_hospital.bronze.exames
COMMENT "Bronze — eventos CDC de exames clínicos a partir do raw em JSON no S3"
TBLPROPERTIES ("quality" = "bronze")
AS
SELECT
  parsed.after.id               AS id,
  parsed.after.paciente_id      AS paciente_id,
  parsed.after.tipo_exame       AS tipo_exame,
  parsed.after.data             AS data_exame,
  parsed.after.resultado        AS resultado,
  parsed.after.created_at       AS created_at,
  parsed.after.updated_at       AS updated_at,

  parsed.op                     AS op,
  parsed.ts_ms                  AS cdc_ts,

  CAST(parsed.op = 'd' AS STRING) AS is_deleted
FROM (
  SELECT
    from_json(
      payload,
      'STRUCT<
        before: STRUCT<id: STRING>,
        after: STRUCT<
          id: STRING,
          paciente_id: STRING,
          tipo_exame: STRING,
          data: STRING,
          resultado: STRING,
          created_at: STRING,
          updated_at: STRING
        >,
        op: STRING,
        ts_ms: STRING
      >'
    ) AS parsed
  FROM cloud_files(
    "${input_path_exames}",
    "json"
  )
);

CREATE OR REFRESH STREAMING LIVE TABLE simulador_oltp_hospital.bronze.internacoes
COMMENT "Bronze — eventos CDC de internações hospitalares a partir do raw em JSON no S3"
TBLPROPERTIES ("quality" = "bronze")
AS
SELECT
  parsed.after.id                AS id,
  parsed.after.paciente_id       AS paciente_id,
  parsed.after.data_entrada      AS data_entrada,
  parsed.after.data_saida        AS data_saida,
  parsed.after.motivo            AS motivo,
  parsed.after.quarto            AS quarto,
  parsed.after.created_at        AS created_at,
  parsed.after.updated_at        AS updated_at,

  parsed.op                      AS op,
  parsed.ts_ms                   AS cdc_ts,

  CAST(parsed.op = 'd' AS STRING) AS is_deleted
FROM (
  SELECT
    from_json(
      payload,
      'STRUCT<
        before: STRUCT<id: STRING>,
        after: STRUCT<
          id: STRING,
          paciente_id: STRING,
          data_entrada: STRING,
          data_saida: STRING,
          motivo: STRING,
          quarto: STRING,
          created_at: STRING,
          updated_at: STRING
        >,
        op: STRING,
        ts_ms: STRING
      >'
    ) AS parsed
  FROM cloud_files(
    "${input_path_internacoes}",
    "json"
  )
);

CREATE OR REFRESH STREAMING LIVE TABLE simulador_oltp_hospital.bronze.pacientes_convenios
COMMENT "Bronze — eventos CDC de vínculo entre pacientes e convênios a partir do raw em JSON no S3"
TBLPROPERTIES ("quality" = "bronze")
AS
SELECT
  parsed.after.id                AS id,
  parsed.after.paciente_id       AS paciente_id,
  parsed.after.convenio_id       AS convenio_id,
  parsed.after.numero_carteira   AS numero_carteira,
  parsed.after.validade          AS validade,
  parsed.after.created_at        AS created_at,
  parsed.after.updated_at        AS updated_at,

  parsed.op                      AS op,
  parsed.ts_ms                   AS cdc_ts,

  CAST(parsed.op = 'd' AS STRING) AS is_deleted
FROM (
  SELECT
    from_json(
      payload,
      'STRUCT<
        before: STRUCT<id: STRING>,
        after: STRUCT<
          id: STRING,
          paciente_id: STRING,
          convenio_id: STRING,
          numero_carteira: STRING,
          validade: STRING,
          created_at: STRING,
          updated_at: STRING
        >,
        op: STRING,
        ts_ms: STRING
      >'
    ) AS parsed
  FROM cloud_files(
    "${input_path_pacientes_convenios}",
    "json"
  )
);
