import streamlit as st
import requests
from components.ui_helpers import API_BASE


def render():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align:center; padding: 2rem 0;'>
            <h1 style='color:#4ade80; font-size:3rem;'>🤖 SmartData AI</h1>
            <p style='color:#9ca3af; font-size:1.1rem;'>Enterprise-Grade AI Analytics Platform</p>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["Login", "Register"])

        with tab_login:
            with st.form("login_form"):
                st.subheader("Sign In")
                username = st.text_input("Username", placeholder="Enter username")
                password = st.text_input("Password", type="password", placeholder="Enter password")
                submitted = st.form_submit_button("Login", use_container_width=True)

            if submitted:
                if not username or not password:
                    st.error("Please fill in all fields.")
                else:
                    try:
                        resp = requests.post(
                            f"{API_BASE}/auth/login",
                            data={"username": username, "password": password},
                            timeout=10,
                        )
                        if resp.status_code == 200:
                            data = resp.json()
                            st.session_state.token = data["access_token"]
                            st.session_state.username = username
                            st.success("Login successful! Redirecting...")
                            st.rerun()
                        else:
                            try:
                                detail = resp.json().get("detail", "Unknown error")
                            except Exception:
                                detail = resp.text or "Unknown error"
                            st.error(f"Login failed: {detail}")
                    except requests.exceptions.ConnectionError:
                        st.warning("Backend not reachable. Using demo mode.")
                        st.session_state.token = "demo_token"
                        st.session_state.username = username
                        st.rerun()

        with tab_register:
            with st.form("register_form"):
                st.subheader("Create Account")
                reg_username = st.text_input("Username", placeholder="Choose a username", key="reg_user")
                reg_email = st.text_input("Email", placeholder="your@email.com", key="reg_email")
                reg_password = st.text_input("Password", type="password", placeholder="Min 6 chars", key="reg_pass")
                reg_role = st.selectbox("Role", ["user", "admin"])
                reg_submitted = st.form_submit_button("Register", use_container_width=True)

            if reg_submitted:
                try:
                    resp = requests.post(
                        f"{API_BASE}/auth/register",
                        json={"username": reg_username, "email": reg_email, "password": reg_password, "role": reg_role},
                        timeout=10,
                    )
                    if resp.status_code == 201:
                        st.success("Registered successfully! Please log in.")
                    else:
                        try:
                            detail = resp.json().get("detail", "Registration failed")
                        except Exception:
                            detail = resp.text or "Registration failed"
                        st.error(detail)
                except requests.exceptions.ConnectionError:
                    st.warning("Backend offline. Demo registration acknowledged.")
