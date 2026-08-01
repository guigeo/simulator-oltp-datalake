from typing import Any, Optional

import psycopg2

from scripts.db_init import create_connection, load_env, load_project_env


DEFAULT_ALERT_RULES = [
    {
        "codigo": "exames_pendentes",
        "titulo": "Exames aguardando resultado",
        "valor_kpi": "exames_pendentes",
        "atencao": 900,
        "critico": 1400,
        "acao": "Acompanhar fila do laboratorio e priorizar exames antigos.",
    },
    {
        "codigo": "consultas_agendadas",
        "titulo": "Agenda futura com alta demanda",
        "valor_kpi": "consultas_agendadas",
        "atencao": 2400,
        "critico": 3200,
        "acao": "Revisar disponibilidade medica e distribuicao por especialidade.",
    },
    {
        "codigo": "internacoes_ativas",
        "titulo": "Internacoes ativas acima da capacidade simulada",
        "valor_kpi": "internacoes_ativas",
        "atencao": 420,
        "critico": 650,
        "acao": "Verificar altas pendentes e ocupacao por quarto.",
    },
    {
        "codigo": "pacientes_sem_convenio",
        "titulo": "Pacientes sem convenio cadastrado",
        "valor_lista": "pacientes_sem_convenio",
        "atencao": 25,
        "critico": 75,
        "acao": "Conferir cadastro financeiro dos pacientes recentes.",
    },
    {
        "codigo": "internacoes_longas",
        "titulo": "Internacoes longas aguardando fechamento",
        "valor_lista": "internacoes_longas",
        "atencao": 25,
        "critico": 60,
        "acao": "Revisar casos ativos com maior tempo de permanencia.",
    },
]


def dashboard_connection() -> psycopg2.extensions.connection:
    """Cria conexao para o dashboard usando config/.env."""
    load_project_env()
    return create_connection(load_env())


def fetch_rows(
    conn: psycopg2.extensions.connection,
    sql: str,
    params: tuple = (),
) -> list[dict[str, Any]]:
    """Executa query e retorna linhas como dicionarios."""
    with conn.cursor() as cur:
        cur.execute(sql, params)
        columns = [col[0] for col in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]


def fetch_one(
    conn: psycopg2.extensions.connection,
    sql: str,
    params: tuple = (),
) -> dict[str, Any]:
    """Executa query e retorna uma linha como dicionario."""
    rows = fetch_rows(conn, sql, params)
    return rows[0] if rows else {}


def get_kpis(conn: psycopg2.extensions.connection) -> dict[str, Any]:
    """Indicadores principais do hospital."""
    return fetch_one(
        conn,
        """
        SELECT
            (SELECT COUNT(*) FROM pacientes) AS pacientes,
            (SELECT COUNT(*) FROM medicos) AS medicos,
            (SELECT COUNT(*) FROM consultas) AS consultas,
            (SELECT COUNT(*) FROM exames) AS exames,
            (
                SELECT COUNT(*)
                FROM internacoes
                WHERE data_saida IS NULL
            ) AS internacoes_ativas,
            (
                SELECT COUNT(*)
                FROM exames
                WHERE resultado IS NULL
            ) AS exames_pendentes,
            (
                SELECT COUNT(*)
                FROM consultas
                WHERE status = 'agendada'
            ) AS consultas_agendadas
        """,
    )


def get_consultas_por_status(
    conn: psycopg2.extensions.connection,
) -> list[dict[str, Any]]:
    """Contagem de consultas por status."""
    return fetch_rows(
        conn,
        """
        SELECT status, COUNT(*) AS total
        FROM consultas
        GROUP BY status
        ORDER BY total DESC
        """,
    )


def get_exames_por_status(
    conn: psycopg2.extensions.connection,
) -> list[dict[str, Any]]:
    """Contagem de exames pendentes e com resultado."""
    return fetch_rows(
        conn,
        """
        SELECT
            CASE
                WHEN resultado IS NULL THEN 'pendente'
                ELSE 'com_resultado'
            END AS status,
            COUNT(*) AS total
        FROM exames
        GROUP BY status
        ORDER BY total DESC
        """,
    )


def get_internacoes_por_status(
    conn: psycopg2.extensions.connection,
) -> list[dict[str, Any]]:
    """Contagem de internacoes abertas e encerradas."""
    return fetch_rows(
        conn,
        """
        SELECT
            CASE
                WHEN data_saida IS NULL THEN 'ativa'
                ELSE 'encerrada'
            END AS status,
            COUNT(*) AS total
        FROM internacoes
        GROUP BY status
        ORDER BY total DESC
        """,
    )


def get_ultimas_consultas(
    conn: psycopg2.extensions.connection,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Ultimas consultas alteradas."""
    return fetch_rows(
        conn,
        """
        SELECT
            c.id,
            c.data,
            c.status,
            p.nome AS paciente,
            m.nome AS medico,
            m.especialidade,
            c.updated_at
        FROM consultas c
        JOIN pacientes p ON p.id = c.paciente_id
        JOIN medicos m ON m.id = c.medico_id
        ORDER BY c.updated_at DESC
        LIMIT %s
        """,
        (limit,),
    )


def get_internacoes_ativas(
    conn: psycopg2.extensions.connection,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Internacoes ativas mais recentes."""
    return fetch_rows(
        conn,
        """
        SELECT
            i.id,
            p.nome AS paciente,
            i.data_entrada,
            i.motivo,
            i.quarto,
            i.updated_at
        FROM internacoes i
        JOIN pacientes p ON p.id = i.paciente_id
        WHERE i.data_saida IS NULL
        ORDER BY i.data_entrada DESC
        LIMIT %s
        """,
        (limit,),
    )


def get_pacientes_sem_convenio(
    conn: psycopg2.extensions.connection,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Pacientes sem convenio associado."""
    return fetch_rows(
        conn,
        """
        SELECT
            p.id,
            p.nome,
            p.cpf,
            p.telefone,
            p.created_at
        FROM pacientes p
        LEFT JOIN pacientes_convenios pc ON pc.paciente_id = p.id
        WHERE pc.id IS NULL
        ORDER BY p.created_at DESC
        LIMIT %s
        """,
        (limit,),
    )


def get_internacoes_longas(
    conn: psycopg2.extensions.connection,
    min_days: int = 7,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Internacoes ativas acima de uma quantidade de dias."""
    return fetch_rows(
        conn,
        """
        SELECT
            i.id,
            p.nome AS paciente,
            i.data_entrada,
            DATE_PART('day', now() - i.data_entrada)::int AS dias_internado,
            i.motivo,
            i.quarto
        FROM internacoes i
        JOIN pacientes p ON p.id = i.paciente_id
        WHERE i.data_saida IS NULL
          AND i.data_entrada <= now() - (%s || ' days')::interval
        ORDER BY dias_internado DESC, i.data_entrada ASC
        LIMIT %s
        """,
        (min_days, limit),
    )


def get_ocupacao_por_quarto(
    conn: psycopg2.extensions.connection,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Ocupacao atual agrupada por quarto."""
    return fetch_rows(
        conn,
        """
        SELECT
            COALESCE(quarto, 'sem_quarto') AS quarto,
            COUNT(*) AS internacoes_ativas
        FROM internacoes
        WHERE data_saida IS NULL
        GROUP BY COALESCE(quarto, 'sem_quarto')
        ORDER BY internacoes_ativas DESC, quarto
        LIMIT %s
        """,
        (limit,),
    )


def get_exames_pendentes_recentes(
    conn: psycopg2.extensions.connection,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Exames pendentes mais recentes."""
    return fetch_rows(
        conn,
        """
        SELECT
            e.id,
            p.nome AS paciente,
            e.tipo_exame,
            e.data,
            e.created_at
        FROM exames e
        JOIN pacientes p ON p.id = e.paciente_id
        WHERE e.resultado IS NULL
        ORDER BY e.data DESC
        LIMIT %s
        """,
        (limit,),
    )


def get_consultas_agendadas_proximas(
    conn: psycopg2.extensions.connection,
    days: int = 7,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Consultas agendadas dentro da janela informada."""
    return fetch_rows(
        conn,
        """
        SELECT
            c.id,
            c.data,
            p.nome AS paciente,
            m.nome AS medico,
            m.especialidade,
            c.motivo
        FROM consultas c
        JOIN pacientes p ON p.id = c.paciente_id
        JOIN medicos m ON m.id = c.medico_id
        WHERE c.status = 'agendada'
          AND c.data BETWEEN now() AND now() + (%s || ' days')::interval
        ORDER BY c.data ASC
        LIMIT %s
        """,
        (days, limit),
    )


def get_operational_alerts(
    snapshot: dict[str, Any],
    thresholds: Optional[dict[str, Any]] = None,
) -> list[dict[str, Any]]:
    """Calcula alertas operacionais calibrados para acompanhamento."""
    thresholds = thresholds or {}
    kpis = snapshot.get("kpis", {})
    alerts = []

    for rule in DEFAULT_ALERT_RULES:
        value = kpis.get(rule["valor_kpi"], 0) if "valor_kpi" in rule else len(
            snapshot.get(rule["valor_lista"], [])
        )
        attention_limit, critical_limit = resolve_alert_limits(rule, thresholds)
        if value <= attention_limit:
            continue

        severity = "crítico" if value > critical_limit else "atenção"
        limit = critical_limit if severity == "crítico" else attention_limit
        alerts.append(
            {
                "codigo": rule["codigo"],
                "titulo": rule["titulo"],
                "valor": value,
                "limite": limit,
                "limite_atencao": attention_limit,
                "limite_critico": critical_limit,
                "severidade": severity,
                "acao": rule["acao"],
                "percentual": round((value / limit) * 100, 1) if limit else 0,
            }
        )

    severity_order = {"crítico": 0, "atenção": 1}
    return sorted(
        alerts,
        key=lambda alert: (severity_order[alert["severidade"]], -alert["valor"]),
    )


def resolve_alert_limits(
    rule: dict[str, Any],
    thresholds: dict[str, Any],
) -> tuple[int, int]:
    """Resolve limites padrao e overrides simples para uma regra."""
    override = thresholds.get(rule["codigo"])
    if isinstance(override, dict):
        attention = int(override.get("atencao", rule["atencao"]))
        critical = int(override.get("critico", rule["critico"]))
    elif override is not None:
        attention = int(override)
        critical = max(attention + 1, int(attention * 2))
    else:
        attention = int(rule["atencao"])
        critical = int(rule["critico"])

    return attention, max(critical, attention + 1)


def get_atividade_recente(
    conn: psycopg2.extensions.connection,
    minutes: int = 15,
) -> list[dict[str, Any]]:
    """Atividade recente por tabela baseada em created_at/updated_at."""
    return fetch_rows(
        conn,
        """
        WITH eventos AS (
            SELECT 'pacientes' AS tabela, created_at, updated_at FROM pacientes
            UNION ALL
            SELECT 'consultas', created_at, updated_at FROM consultas
            UNION ALL
            SELECT 'exames', created_at, updated_at FROM exames
            UNION ALL
            SELECT 'internacoes', created_at, updated_at FROM internacoes
            UNION ALL
            SELECT 'pacientes_convenios', created_at, updated_at
            FROM pacientes_convenios
        )
        SELECT
            tabela,
            COUNT(*) FILTER (
                WHERE created_at >= now() - (%s || ' minutes')::interval
            ) AS criados,
            COUNT(*) FILTER (
                WHERE updated_at >= now() - (%s || ' minutes')::interval
                  AND updated_at > created_at
            ) AS atualizados
        FROM eventos
        GROUP BY tabela
        ORDER BY tabela
        """,
        (minutes, minutes),
    )


def get_dashboard_snapshot(
    conn: psycopg2.extensions.connection,
    recent_minutes: int = 15,
) -> dict[str, Any]:
    """Retorna todos os dados necessarios para uma renderizacao do dashboard."""
    return {
        "kpis": get_kpis(conn),
        "consultas_por_status": get_consultas_por_status(conn),
        "exames_por_status": get_exames_por_status(conn),
        "internacoes_por_status": get_internacoes_por_status(conn),
        "ultimas_consultas": get_ultimas_consultas(conn),
        "internacoes_ativas": get_internacoes_ativas(conn),
        "internacoes_longas": get_internacoes_longas(conn),
        "ocupacao_por_quarto": get_ocupacao_por_quarto(conn),
        "exames_pendentes_recentes": get_exames_pendentes_recentes(conn),
        "consultas_agendadas_proximas": get_consultas_agendadas_proximas(conn),
        "pacientes_sem_convenio": get_pacientes_sem_convenio(conn),
        "atividade_recente": get_atividade_recente(conn, recent_minutes),
    }
