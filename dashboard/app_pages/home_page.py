import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from components.ui_helpers import api_get, metric_card


def render():
    st.title("Dashboard Overview")
    st.caption("Real-time insights from your data pipeline")

    # KPIs row
    kpis = api_get("analytics/kpis")
    if kpis and "error" not in kpis:
        cols = st.columns(4)
        kpi_items = [
            ("Total Records", str(kpis.get("total_records", "—")), "#4ade80"),
            ("Clean Records", str(kpis.get("clean_records", "—")), "#06b6d4"),
            ("Missing Rate", f"{kpis.get('missing_rate_pct', 0)}%", "#facc15"),
            ("Numeric Cols", str(kpis.get("numeric_columns", "—")), "#a78bfa"),
        ]
        for col, (title, value, color) in zip(cols, kpi_items):
            with col:
                metric_card(title, value, color=color)
    else:
        st.info("Upload a dataset to see KPIs. Running in demo mode.")
        cols = st.columns(4)
        demo = [("Total Records", "10,234", "#4ade80"), ("Clean Records", "9,891", "#06b6d4"),
                ("Missing Rate", "2.4%", "#facc15"), ("Numeric Cols", "8", "#a78bfa")]
        for col, (t, v, c) in zip(cols, demo):
            with col:
                metric_card(t, v, color=c)

    st.divider()

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("ETL Pipeline Activity")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(1, 13)),
            y=[120, 450, 380, 620, 540, 780, 920, 1100, 850, 1300, 1150, 1400],
            mode="lines+markers",
            line=dict(color="#4ade80", width=3),
            marker=dict(size=8, color="#4ade80"),
            name="Records Processed",
            fill="tozeroy",
            fillcolor="rgba(74,222,128,0.1)",
        ))
        fig.update_layout(
            plot_bgcolor="#16213e", paper_bgcolor="#0f0f1a",
            font_color="#e2e8f0", height=280,
            xaxis=dict(showgrid=False, title="Month"),
            yaxis=dict(showgrid=True, gridcolor="#1e3a5f", title="Records"),
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("Data Health")
        labels = ["Clean", "Missing", "Duplicates"]
        values = [85, 10, 5]
        fig_pie = go.Figure(go.Pie(
            labels=labels, values=values,
            marker_colors=["#4ade80", "#facc15", "#f87171"],
            hole=0.5,
        ))
        fig_pie.update_layout(
            plot_bgcolor="#16213e", paper_bgcolor="#0f0f1a",
            font_color="#e2e8f0", height=280,
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=True,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    st.divider()

    # Model metrics
    st.subheader("ML Model Status")
    metrics = api_get("predict/model/accuracy")
    if metrics and "accuracy" in metrics:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            metric_card("Accuracy", f"{metrics['accuracy']*100:.1f}%", color="#4ade80")
        with c2:
            metric_card("Precision", f"{metrics['precision']*100:.1f}%", color="#06b6d4")
        with c3:
            metric_card("Recall", f"{metrics['recall']*100:.1f}%", color="#a78bfa")
        with c4:
            metric_card("F1 Score", f"{metrics['f1_score']*100:.1f}%", color="#facc15")
    else:
        st.info("Train a model to see ML metrics here.")

    # Uploaded files
    st.divider()
    st.subheader("Recent Uploads")
    files = api_get("upload/files")
    if files and files.get("files"):
        df = pd.DataFrame(files["files"])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No files uploaded yet. Go to Upload Data.")
