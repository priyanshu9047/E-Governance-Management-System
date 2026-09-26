"""
Utility functions for Streamlit frontend — API communication.
"""

import requests
import streamlit as st

API_BASE = "http://127.0.0.1:8000/api"


def get_headers():
    """Get auth headers from session state."""
    token = st.session_state.get("token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def api_get(endpoint: str, params: dict = None):
    """Make an authenticated GET request."""
    try:
        resp = requests.get(f"{API_BASE}{endpoint}", headers=get_headers(), params=params, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 401:
            st.session_state.clear()
            st.error("Session expired. Please login again.")
            return None
        else:
            detail = resp.json().get("detail", "Unknown error")
            st.error(f"Error: {detail}")
            return None
    except requests.ConnectionError:
        st.error("⚠️ Cannot connect to the backend server. Make sure FastAPI is running on port 8000.")
        return None


def api_post(endpoint: str, data: dict = None, files: dict = None):
    """Make an authenticated POST request."""
    try:
        kwargs = {"headers": get_headers(), "timeout": 10}
        if files:
            kwargs["data"] = data
            kwargs["files"] = files
        else:
            kwargs["json"] = data

        resp = requests.post(f"{API_BASE}{endpoint}", **kwargs)
        if resp.status_code in (200, 201):
            return resp.json()
        elif resp.status_code == 401:
            st.session_state.clear()
            st.error("Session expired. Please login again.")
            return None
        else:
            detail = resp.json().get("detail", "Unknown error")
            st.error(f"Error: {detail}")
            return None
    except requests.ConnectionError:
        st.error("⚠️ Cannot connect to the backend server.")
        return None


def api_put(endpoint: str, data: dict = None):
    """Make an authenticated PUT request."""
    try:
        resp = requests.put(f"{API_BASE}{endpoint}", headers=get_headers(), json=data, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        else:
            detail = resp.json().get("detail", "Unknown error")
            st.error(f"Error: {detail}")
            return None
    except requests.ConnectionError:
        st.error("⚠️ Cannot connect to the backend server.")
        return None


def is_logged_in():
    """Check if user is logged in."""
    return st.session_state.get("token") is not None


def require_login():
    """Redirect to login if not authenticated."""
    if not is_logged_in():
        st.warning("🔒 Please login to access this page.")
        st.stop()


def require_officer():
    """Require officer or admin role."""
    require_login()
    role = st.session_state.get("role", "")
    if role not in ("officer", "admin"):
        st.error("🚫 Access denied. Officer/Admin only.")
        st.stop()
