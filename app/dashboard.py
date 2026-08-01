import time
from datetime import datetime

import streamlit as st

from app.dashboard_data import (
    dashboard_connection,
    get_dashboard_snapshot,
    get_operational_alerts,
)


st.set_page_config(
    page_title="Hospital OLTP",
    page_icon="H",
    layout="wide",
)


def render_metric(label: str, value: object) -> None:
    st.metric(label, f"{value:,}".replace(",", "."))


def render_status_table(title: str, rows: list[dict]) -> None:
    st.subheader(title)
    if rows:
        st.dataframe(rows, hide_index=True, use_container_width=True)
    else:
        st.info("Sem dados para exibir.")


def render_alerts(alerts: list[dict]) -> None:
    st.subheader("Alertas operacionais")
    if not alerts:
        st.success("Nenhum alerta operacional ativo.")
        return

    for alert in alerts:
        message = (
            f"{alert['titulo']}: {alert['valor']} "
            f"(limite {alert['limite']})"
        )
        if alert["severidade"] == "crítico":
            st.error(message)
        else:
            st.warning(message)


def render_overview(snapshot: dict, recent_minutes: int) -> None:
    kpis = snapshot["kpis"]
    cols = st.columns(7)
    with cols[0]:
        render_metric("Pacientes", kpis.get("pacientes", 0))
    with cols[1]:
        render_metric("Medicos", kpis.get("medicos", 0))
    with cols[2]:
        render_metric("Consultas", kpis.get("consultas", 0))
    with cols[3]:
        render_metric("Agendadas", kpis.get("consultas_agendadas", 0))
    with cols[4]:
        render_metric("Exames", kpis.get("exames", 0))
    with cols[5]:
        render_metric("Pendentes", kpis.get("exames_pendentes", 0))
    with cols[6]:
        render_metric("Internacoes", kpis.get("internacoes_ativas", 0))

    render_alerts(get_operational_alerts(snapshot))

    left, middle, right = st.columns(3)
    with left:
        render_status_table("Consultas por status", snapshot["consultas_por_status"])
    with middle:
        render_status_table("Exames por status", snapshot["exames_por_status"])
    with right:
        render_status_table("Internacoes por status", snapshot["internacoes_por_status"])

    st.subheader(f"Atividade nos ultimos {recent_minutes} minutos")
    st.dataframe(
        snapshot["atividade_recente"],
        hide_index=True,
        use_container_width=True,
    )


def render_consultas(snapshot: dict) -> None:
    left, right = st.columns(2)
    with left:
        render_status_table("Consultas por status", snapshot["consultas_por_status"])
    with right:
        render_status_table(
            "Agendadas nos próximos 7 dias",
            snapshot["consultas_agendadas_proximas"],
        )

    render_status_table("Ultimas consultas alteradas", snapshot["ultimas_consultas"])


def render_exames(snapshot: dict) -> None:
    left, right = st.columns(2)
    with left:
        render_status_table("Exames por status", snapshot["exames_por_status"])
    with right:
        render_status_table(
            "Exames pendentes recentes",
            snapshot["exames_pendentes_recentes"],
        )


def render_internacoes(snapshot: dict) -> None:
    left, right = st.columns(2)
    with left:
        render_status_table("Internacoes por status", snapshot["internacoes_por_status"])
    with right:
        render_status_table("Ocupacao por quarto", snapshot["ocupacao_por_quarto"])

    left, right = st.columns(2)
    with left:
        render_status_table("Internacoes ativas", snapshot["internacoes_ativas"])
    with right:
        render_status_table("Internacoes longas", snapshot["internacoes_longas"])


def render_atividade(snapshot: dict, recent_minutes: int) -> None:
    render_status_table(
        f"Atividade nos ultimos {recent_minutes} minutos",
        snapshot["atividade_recente"],
    )
    render_status_table("Pacientes sem convenio", snapshot["pacientes_sem_convenio"])


def main() -> None:
    st.title("Hospital OLTP")

    with st.sidebar:
        st.header("Atualizacao")
        auto_refresh = st.toggle("Atualizar automaticamente", value=True)
        refresh_seconds = st.slider("Intervalo", 2, 30, 5, 1)
        recent_minutes = st.slider("Janela de atividade", 5, 120, 15, 5)
        st.caption(f"Ultima leitura: {datetime.now():%d/%m/%Y %H:%M:%S}")

    try:
        conn = dashboard_connection()
        try:
            snapshot = get_dashboard_snapshot(conn, recent_minutes=recent_minutes)
        finally:
            conn.close()
    except Exception as exc:
        st.error(f"Falha ao carregar dados do PostgreSQL: {exc}")
        st.stop()

    tabs = st.tabs([
        "Visao geral",
        "Consultas",
        "Exames",
        "Internacoes",
        "Atividade",
    ])
    with tabs[0]:
        render_overview(snapshot, recent_minutes)
    with tabs[1]:
        render_consultas(snapshot)
    with tabs[2]:
        render_exames(snapshot)
    with tabs[3]:
        render_internacoes(snapshot)
    with tabs[4]:
        render_atividade(snapshot, recent_minutes)

    if auto_refresh:
        time.sleep(refresh_seconds)
        st.rerun()


if __name__ == "__main__":
    main()
