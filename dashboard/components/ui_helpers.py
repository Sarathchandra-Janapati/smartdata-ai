import streamlit as st
import requests
from typing import Optional, Dict, Any

API_BASE = "http://localhost:8000/api"


def auth_headers() -> Dict[str, str]:
    token = st.session_state.get("token", "")
    return {"Authorization": f"Bearer {token}"}


def api_get(endpoint: str, params: dict = None) -> Optional[Dict]:
    try:
        resp = requests.get(f"{API_BASE}/{endpoint}", headers=auth_headers(), params=params, timeout=15)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        return None
    except Exception as e:
        st.error(f"API error: {e}")
        return None


def api_post(endpoint: str, json_data: dict = None, files=None) -> Optional[Dict]:
    try:
        resp = requests.post(f"{API_BASE}/{endpoint}", headers=auth_headers(), json=json_data, files=files, timeout=30)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        return None
    except Exception as e:
        st.error(f"API error: {e}")
        return None


def metric_card(title: str, value: str, delta: str = "", color: str = "#4ade80"):
    st.markdown(f"""
    <div class='metric-card' style='border-left-color:{color};'>
        <div class='metric-title'>{title}</div>
        <div class='metric-value' style='color:{color};'>{value}</div>
        {"<div style='color:#9ca3af; font-size:0.8rem;'>" + delta + "</div>" if delta else ""}
    </div>
    """, unsafe_allow_html=True)


def status_badge(status: str) -> str:
    colors_map = {
        "completed": "#4ade80",
        "running": "#facc15",
        "failed": "#f87171",
        "pending": "#60a5fa",
    }
    color = colors_map.get(status.lower(), "#9ca3af")
    return f"<span style='background:{color}20; color:{color}; padding:2px 8px; border-radius:4px; font-size:0.8rem;'>{status.upper()}</span>"
