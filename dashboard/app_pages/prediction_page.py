import streamlit as st
import plotly.graph_objects as go
from components.ui_helpers import api_get, api_post, metric_card


def render():
    st.title("AI Predictions")
    st.caption("Run ML inference on the trained model")

    col_form, col_result = st.columns([1, 1])

    with col_form:
        st.subheader("Input Features")

        # Get model info
        metrics = api_get("predict/model/accuracy")
        if metrics and "features" in metrics:
            features = metrics["features"][:8]
            st.caption(f"Model: {metrics.get('model_type', 'RandomForest')} | Features: {len(features)}")
        else:
            features = ["tenure", "monthly_charges", "total_charges", "contract_type",
                        "internet_service", "payment_method", "num_products", "support_calls"]
            st.caption("Demo mode: Using sample features")

        inputs = {}
        for feat in features:
            if any(k in feat for k in ["charge", "amount", "salary", "age", "tenure", "score"]):
                inputs[feat] = st.number_input(feat.replace("_", " ").title(), value=50.0, step=1.0)
            else:
                inputs[feat] = st.number_input(feat.replace("_", " ").title(), value=1.0, step=1.0)

        run_btn = st.button("Run Prediction", type="primary", use_container_width=True)

    with col_result:
        st.subheader("Prediction Result")

        if run_btn:
            with st.spinner("Running inference..."):
                result = api_post("predict/", json_data={"features": inputs})

                if result:
                    label = result.get("label", str(result.get("prediction", "?")))
                    confidence = result.get("confidence", 0)

                    # Result badge
                    color = "#f87171" if "1" in str(result.get("prediction", "")) or label.lower() in ["yes", "churn", "1"] else "#4ade80"
                    st.markdown(f"""
                    <div style='background:linear-gradient(135deg,#16213e,#0f3460); padding:1.5rem;
                                border-radius:12px; border-left:5px solid {color}; margin-bottom:1rem;'>
                        <div style='color:#9ca3af; font-size:0.9rem;'>Prediction</div>
                        <div style='color:{color}; font-size:2.5rem; font-weight:800;'>{label}</div>
                        <div style='color:#9ca3af; margin-top:0.5rem;'>Confidence: <b style='color:#facc15;'>{confidence*100:.1f}%</b></div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Confidence gauge
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=confidence * 100,
                        title={"text": "Confidence %", "font": {"color": "#e2e8f0"}},
                        number={"suffix": "%", "font": {"color": "#4ade80"}},
                        gauge={
                            "axis": {"range": [0, 100], "tickcolor": "#9ca3af"},
                            "bar": {"color": "#4ade80"},
                            "bgcolor": "#16213e",
                            "steps": [
                                {"range": [0, 50], "color": "rgba(248,113,113,0.12)"},
                                {"range": [50, 80], "color": "rgba(250,204,21,0.12)"},
                                {"range": [80, 100], "color": "rgba(74,222,128,0.12)"},
                            ],
                            "threshold": {"line": {"color": "#4ade80", "width": 3}, "value": confidence * 100},
                        },
                    ))
                    fig.update_layout(
                        plot_bgcolor="#0f0f1a", paper_bgcolor="#0f0f1a",
                        height=280, margin=dict(l=20, r=20, t=40, b=10),
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # Probabilities
                    if "probabilities" in result:
                        st.subheader("Class Probabilities")
                        probs = result["probabilities"]
                        fig2 = go.Figure(go.Bar(
                            x=list(probs.keys()),
                            y=[v * 100 for v in probs.values()],
                            marker_color=["#4ade80", "#f87171"][:len(probs)],
                            text=[f"{v*100:.1f}%" for v in probs.values()],
                            textposition="auto",
                        ))
                        fig2.update_layout(
                            plot_bgcolor="#16213e", paper_bgcolor="#0f0f1a",
                            font_color="#e2e8f0", height=240,
                            yaxis_title="Probability (%)",
                            margin=dict(l=10, r=10, t=10, b=10),
                        )
                        st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.warning("Backend offline. Showing demo prediction.")
                    st.success("Demo Prediction: **No Churn** (Confidence: 87.3%)")

        else:
            st.markdown("""
            <div style='text-align:center; color:#9ca3af; padding:3rem;'>
                <div style='font-size:3rem;'>🤖</div>
                <p>Fill in the feature values and click<br><strong style='color:#4ade80;'>Run Prediction</strong></p>
            </div>
            """, unsafe_allow_html=True)

    # Model metrics section
    st.divider()
    st.subheader("Model Performance Metrics")
    metrics = api_get("predict/model/accuracy")
    if metrics and "accuracy" in metrics:
        c1, c2, c3, c4 = st.columns(4)
        colors_map = [("#4ade80", "accuracy"), ("#06b6d4", "precision"), ("#a78bfa", "recall"), ("#facc15", "f1_score")]
        for col, (color, key) in zip([c1, c2, c3, c4], colors_map):
            with col:
                metric_card(key.replace("_", " ").title(), f"{metrics[key]*100:.1f}%", color=color)
    else:
        st.info("Train a model first. Run `python -m backend.app.ml.train_model` from the project root.")
