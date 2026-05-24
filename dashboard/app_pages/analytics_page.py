import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from components.ui_helpers import api_get


def render():
    st.title("Analytics")
    st.caption("Visual analytics from your processed data")

    charts = api_get("analytics/charts")
    summary = api_get("analytics/summary")

    if not charts or "error" in str(charts):
        st.info("No analytics data found. Upload a dataset first. Showing demo charts below.")
        _render_demo_charts()
        return

    # Bar chart
    if "bar_chart" in charts:
        d = charts["bar_chart"]
        st.subheader(d["title"])
        fig = go.Figure(go.Bar(
            x=d["x"], y=d["y"],
            marker_color=["#4ade80"] * len(d["x"]),
            text=d["y"], textposition="auto",
        ))
        fig.update_layout(
            plot_bgcolor="#16213e", paper_bgcolor="#0f0f1a",
            font_color="#e2e8f0", height=350,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#1e3a5f"),
            margin=dict(l=20, r=20, t=30, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        if "line_chart" in charts:
            d = charts["line_chart"]
            st.subheader(d["title"])
            fig = go.Figure(go.Scatter(
                x=d["x"], y=d["y"], mode="lines",
                line=dict(color="#06b6d4", width=2),
                fill="tozeroy", fillcolor="rgba(6,182,212,0.1)",
            ))
            fig.update_layout(
                plot_bgcolor="#16213e", paper_bgcolor="#0f0f1a",
                font_color="#e2e8f0", height=280,
                margin=dict(l=10, r=10, t=30, b=10),
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if "histogram" in charts:
            d = charts["histogram"]
            st.subheader(d["title"])
            fig = go.Figure(go.Bar(
                x=d["bins"][:-1], y=d["counts"],
                marker_color="#a78bfa",
            ))
            fig.update_layout(
                plot_bgcolor="#16213e", paper_bgcolor="#0f0f1a",
                font_color="#e2e8f0", height=280,
                margin=dict(l=10, r=10, t=30, b=10),
            )
            st.plotly_chart(fig, use_container_width=True)

    # Correlation heatmap
    if "correlation" in charts:
        d = charts["correlation"]
        st.subheader(d["title"])
        fig = go.Figure(go.Heatmap(
            z=d["matrix"], x=d["columns"], y=d["columns"],
            colorscale="RdYlGn", zmid=0,
            text=[[f"{v:.2f}" for v in row] for row in d["matrix"]],
            texttemplate="%{text}",
        ))
        fig.update_layout(
            plot_bgcolor="#16213e", paper_bgcolor="#0f0f1a",
            font_color="#e2e8f0", height=400,
            margin=dict(l=20, r=20, t=30, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)

    # Data table
    if summary and "describe" in summary:
        st.subheader("Statistical Summary")
        desc_df = pd.DataFrame(summary["describe"]).T
        st.dataframe(desc_df.round(4), use_container_width=True)


def _render_demo_charts():
    np.random.seed(42)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Demo: Sales by Category")
        fig = go.Figure(go.Bar(
            x=["Electronics", "Clothing", "Food", "Books", "Sports"],
            y=[45000, 32000, 28000, 15000, 22000],
            marker_color=["#4ade80", "#06b6d4", "#a78bfa", "#facc15", "#f87171"],
        ))
        fig.update_layout(plot_bgcolor="#16213e", paper_bgcolor="#0f0f1a", font_color="#e2e8f0", height=300)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Demo: Monthly Revenue")
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
        revenue = [12000, 15000, 11000, 18000, 22000, 19000]
        fig = go.Figure(go.Scatter(x=months, y=revenue, mode="lines+markers",
                                   line=dict(color="#4ade80", width=3), fill="tozeroy",
                                   fillcolor="rgba(74,222,128,0.1)"))
        fig.update_layout(plot_bgcolor="#16213e", paper_bgcolor="#0f0f1a", font_color="#e2e8f0", height=300)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Demo: Correlation Heatmap")
    cols = ["Age", "Salary", "Experience", "Score", "Churn"]
    matrix = np.random.uniform(-1, 1, (5, 5))
    np.fill_diagonal(matrix, 1)
    fig = go.Figure(go.Heatmap(z=matrix.tolist(), x=cols, y=cols, colorscale="RdYlGn", zmid=0))
    fig.update_layout(plot_bgcolor="#16213e", paper_bgcolor="#0f0f1a", font_color="#e2e8f0", height=380)
    st.plotly_chart(fig, use_container_width=True)
