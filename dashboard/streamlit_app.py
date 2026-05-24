import streamlit as st

st.set_page_config(
    page_title="SmartData AI Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #0f0f1a; }
    [data-testid="stSidebar"] { background-color: #1a1a2e; }
    .metric-card {
        background: linear-gradient(135deg, #16213e 0%, #0f3460 100%);
        padding: 1.2rem; border-radius: 12px; border-left: 4px solid #4ade80;
        margin-bottom: 0.8rem;
    }
    .metric-title { color: #9ca3af; font-size: 0.85rem; margin-bottom: 4px; }
    .metric-value { color: #4ade80; font-size: 2rem; font-weight: 700; }
    h1, h2, h3 { color: #e2e8f0 !important; }
    .stButton > button {
        background: linear-gradient(135deg, #4ade80, #06b6d4);
        color: #0f0f1a; border: none; border-radius: 8px;
        font-weight: 700; padding: 0.5rem 1.5rem;
    }
    .stButton > button:hover { opacity: 0.85; }
</style>
""", unsafe_allow_html=True)

# ── Session state init ─────────────────────────────────────────────────────────
if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None


# ── Sidebar navigation ─────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/color/96/artificial-intelligence.png", width=64)
    st.title("SmartData AI")
    st.caption("AI-Powered ETL Platform")
    st.divider()

    if st.session_state.token:
        st.success(f"Logged in as **{st.session_state.username}**")
        nav = st.radio(
            "Navigation",
            ["Dashboard", "Upload Data", "Analytics", "AI Predictions", "Reports"],
            label_visibility="collapsed",
            key="nav_selection",
        )
        st.divider()
        if st.button("Logout"):
            st.session_state.token = None
            st.session_state.username = None
            st.rerun()
    else:
        nav = "Login"

# ── Page routing ───────────────────────────────────────────────────────────────
try:
    if nav == "Login" or not st.session_state.token:
        from app_pages import login_page
        login_page.render()

    elif nav == "Dashboard":
        from app_pages import home_page
        home_page.render()

    elif nav == "Upload Data":
        from app_pages import upload_page
        upload_page.render()

    elif nav == "Analytics":
        from app_pages import analytics_page
        analytics_page.render()

    elif nav == "AI Predictions":
        from app_pages import prediction_page
        prediction_page.render()

    elif nav == "Reports":
        from app_pages import reports_page
        reports_page.render()

except Exception as e:
    st.error(f"Page error: {e}")
    import traceback
    st.code(traceback.format_exc())
