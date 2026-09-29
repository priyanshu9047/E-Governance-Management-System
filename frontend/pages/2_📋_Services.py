"""
Services Page — Browse available government services.
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from frontend.utils import api_get

st.set_page_config(page_title="Services | E-Gov Portal", page_icon="📋", layout="wide")

st.markdown("# 📋 Government Services")
st.markdown("Browse all available government services and their requirements.")
st.markdown("---")

# Filters
col1, col2 = st.columns(2)

with col1:
    departments = api_get("/services/departments")
    dept_options = {"All Departments": None}
    if departments:
        for d in departments:
            dept_options[d["name"]] = d["department_id"]
    selected_dept_name = st.selectbox("🏢 Filter by Department", list(dept_options.keys()))
    selected_dept = dept_options[selected_dept_name]

with col2:
    categories = api_get("/services/categories")
    cat_options = ["All Categories"] + (categories or [])
    selected_cat = st.selectbox("🏷️ Filter by Category", cat_options)

# Fetch services
params = {}
if selected_dept:
    params["department_id"] = selected_dept
if selected_cat != "All Categories":
    params["category"] = selected_cat

services = api_get("/services/", params=params)

if services:
    st.markdown(f"**Showing {len(services)} service(s)**")
    st.markdown("---")

    for svc in services:
        with st.expander(f"📄 {svc['name']} — {svc.get('department_name', '')} | ₹{svc['fee']:.2f}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**Category:** {svc.get('category', 'N/A')}")
                st.markdown(f"**Department:** {svc.get('department_name', 'N/A')}")
            with col2:
                st.markdown(f"**Fee:** ₹{svc['fee']:.2f}")
                st.markdown(f"**Processing Time:** {svc['processing_days']} days")
            with col3:
                st.markdown(f"**Service ID:** {svc['service_id']}")
                st.markdown(f"**Status:** {'🟢 Active' if svc['is_active'] else '🔴 Inactive'}")

            if svc.get("description"):
                st.markdown(f"**Description:** {svc['description']}")

            # Show requirements
            reqs = api_get(f"/services/{svc['service_id']}/requirements")
            if reqs:
                st.markdown("**📎 Required Documents:**")
                for req in reqs:
                    mandatory = "🔴 Mandatory" if req["is_mandatory"] else "🟡 Optional"
                    st.markdown(f"- {req['document_name']} ({mandatory})")
            else:
                st.markdown("*No specific document requirements listed.*")

            if st.button("📝 Apply for this service", key=f"apply_{svc['service_id']}", use_container_width=True):
                st.session_state["prefill_service_id"] = svc['service_id']
                st.switch_page("pages/3_📝_Apply.py")
else:
    st.info("No services found matching your filters.")
