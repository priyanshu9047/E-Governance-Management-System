"""
Complaints Page — Raise and track complaints.
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from frontend.utils import api_get, api_post, require_login

st.set_page_config(page_title="Complaints | E-Gov Portal", page_icon="🗣️", layout="wide")

require_login()

st.markdown("# 🗣️ Complaints")
st.markdown("Raise a complaint or track existing ones.")
st.markdown("---")

tab1, tab2 = st.tabs(["📝 Raise Complaint", "📋 My Complaints"])

with tab1:
    st.subheader("Raise a New Complaint")

    with st.form("complaint_form"):
        subject = st.text_input("Subject *", placeholder="Brief description of the issue")
        description = st.text_area("Description *", placeholder="Explain the issue in detail (min 10 characters)")

        col1, col2 = st.columns(2)
        with col1:
            priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
        with col2:
            # Optionally link to an application
            apps = api_get("/applications/my")
            app_options = {"None (General Complaint)": None}
            if apps:
                for a in apps:
                    app_options[f"{a['application_ref']} — {a.get('service_name', '')}"] = a["application_id"]
            linked_app = st.selectbox("Link to Application (Optional)", list(app_options.keys()))

        submitted = st.form_submit_button("📨 Submit Complaint", use_container_width=True)

        if submitted:
            if not subject or len(subject) < 5:
                st.error("Subject must be at least 5 characters.")
            elif not description or len(description) < 10:
                st.error("Description must be at least 10 characters.")
            else:
                result = api_post("/complaints/", {
                    "subject": subject,
                    "description": description,
                    "priority": priority,
                    "application_id": app_options[linked_app],
                })
                if result:
                    st.success(f"✅ Complaint `{result['complaint_ref']}` submitted successfully!")
                    st.rerun()

with tab2:
    st.subheader("My Complaints")
    complaints = api_get("/complaints/my")

    if complaints:
        for c in complaints:
            status_colors = {"Open": "🔴", "In Progress": "🟡", "Resolved": "🟢", "Closed": "⚫"}
            icon = status_colors.get(c["status"], "⚪")

            with st.expander(f"{icon} {c['complaint_ref']} — {c['subject']} [{c['status']}]"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Status:** {c['status']}")
                    st.markdown(f"**Priority:** {c['priority']}")
                with col2:
                    st.markdown(f"**Created:** {c.get('created_at', 'N/A')}")
                    if c.get("resolved_at"):
                        st.markdown(f"**Resolved:** {c['resolved_at']}")

                st.markdown(f"**Description:** {c['description']}")
                if c.get("application_id"):
                    st.markdown(f"**Linked Application:** #{c['application_id']}")
    else:
        st.info("No complaints filed yet.")
