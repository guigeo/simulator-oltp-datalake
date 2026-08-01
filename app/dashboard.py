import time
from datetime import datetime

import streamlit as st

from app.dashboard_data import dashboard_connection, get_dashboard_snapshot


st.set_page_config(
    page_title="Hospital Ops",
    page_icon="",
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


def main() -> None:
    st.title("Hospital Ops")

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

    recent_left, recent_right = st.columns(2)
    with recent_left:
        render_status_table("Ultimas consultas", snapshot["ultimas_consultas"])
    with recent_right:
        render_status_table("Internacoes ativas", snapshot["internacoes_ativas"])

    if auto_refresh:
        time.sleep(refresh_seconds)
        st.rerun()


if __name__ == "__main__":
    main()
