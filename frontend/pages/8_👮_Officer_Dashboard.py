"""
Officer Dashboard Page — Process applications, view analytics.
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from frontend.utils import api_get, api_put, require_officer

st.set_page_config(page_title="Officer Dashboard | E-Gov Portal", page_icon="👮", layout="wide")

require_officer()

st.markdown("# 👮 Officer / Admin Dashboard")
st.markdown("Process applications, manage complaints, and view analytics.")
st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Pending Applications",
    "📊 Analytics",
    "🗣️ Complaints",
    "👥 Officer Performance"
])

# ── Tab 1: Pending Applications ────────────────────────────────────────────────
with tab1:
    st.subheader("📋 Applications Awaiting Action")

    pending = api_get("/applications/pending")
    if pending:
        for app in pending:
            with st.expander(
                f"🔹 {app['application_ref']} — {app.get('service_name', 'N/A')} | "
                f"Status: {app['status']} | Citizen: {app.get('citizen_name', 'N/A')}"
            ):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Application ID:** {app['application_id']}")
                    st.markdown(f"**Citizen:** {app.get('citizen_name', 'N/A')}")
                    st.markdown(f"**Service:** {app.get('service_name', 'N/A')}")
                    st.markdown(f"**Department:** {app.get('department_name', 'N/A')}")
                with col2:
                    st.markdown(f"**Current Status:** {app['status']}")
                    st.markdown(f"**Submitted:** {app.get('submitted_at', 'N/A')}")
                    if app.get('remarks'):
                        st.markdown(f"**Remarks:** {app['remarks']}")

                # View documents
                docs = api_get(f"/documents/application/{app['application_id']}")
                if docs:
                    st.markdown("**📎 Uploaded Documents:**")
                    for d in docs:
                        st.markdown(f"- {d['document_name']} ({d.get('file_type', 'N/A')}, {d.get('file_size_kb', 0)} KB)")

                st.markdown("---")
                st.markdown("**🔧 Update Status:**")
                col1, col2 = st.columns(2)
                with col1:
                    new_status = st.selectbox(
                        "New Status",
                        ["Under Review", "Documents Verified", "Approved", "Rejected", "Returned"],
                        key=f"status_{app['application_id']}",
                    )
                with col2:
                    remarks = st.text_input("Remarks", key=f"remarks_{app['application_id']}", placeholder="Optional remarks")

                if st.button("✅ Update", key=f"update_{app['application_id']}", use_container_width=True):
                    result = api_put(
                        f"/applications/{app['application_id']}/status",
                        {"status": new_status, "remarks": remarks or None},
                    )
                    if result:
                        st.success(f"Application {app['application_ref']} updated to '{new_status}'!")
                        st.rerun()
    else:
        st.info("No pending applications.")

# ── Tab 2: Analytics ───────────────────────────────────────────────────────────
with tab2:
    st.subheader("📊 System Analytics")

    stats = api_get("/admin/stats")
    if stats:
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("📋 Total", stats["total_applications"])
        with col2:
            st.metric("✅ Approved", stats["approved"])
        with col3:
            st.metric("⏳ Pending", stats["pending"])
        with col4:
            st.metric("❌ Rejected", stats["rejected"])
        with col5:
            st.metric("📅 Avg Days", stats.get("avg_processing_days", "N/A"))

    st.markdown("---")

    # Status distribution chart
    st.markdown("### 📈 Status Distribution")
    status_data = api_get("/admin/status-distribution")
    if status_data:
        import plotly.express as px
        import pandas as pd
        df = pd.DataFrame(status_data)
        fig = px.pie(df, names="status", values="count", title="Application Status Distribution",
                     color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig, use_container_width=True)

    # Department summary
    st.markdown("### 🏢 Department-wise Summary")
    dept_data = api_get("/admin/department-summary")
    if dept_data:
        import pandas as pd
        df = pd.DataFrame(dept_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Bar chart
        import plotly.express as px
        fig = px.bar(df, x="department_name", y=["approved", "rejected", "pending", "under_review"],
                     title="Department-wise Application Breakdown",
                     barmode="group",
                     color_discrete_sequence=["#10b981", "#ef4444", "#f59e0b", "#3b82f6"])
        st.plotly_chart(fig, use_container_width=True)

    # Service ranking
    st.markdown("### 🏆 Service Popularity Ranking")
    ranking = api_get("/admin/service-ranking")
    if ranking:
        import pandas as pd
        df = pd.DataFrame(ranking)
        st.dataframe(df, use_container_width=True, hide_index=True)

    # Monthly trend
    st.markdown("### 📅 Monthly Application Trend")
    monthly = api_get("/admin/monthly-trend")
    if monthly:
        import plotly.express as px
        import pandas as pd
        df = pd.DataFrame(monthly)
        fig = px.line(df, x="month", y="applications_count", title="Monthly Applications",
                      markers=True, color_discrete_sequence=["#667eea"])
        st.plotly_chart(fig, use_container_width=True)

# ── Tab 3: Complaints ─────────────────────────────────────────────────────────
with tab3:
    st.subheader("🗣️ Complaints Management")

    complaint_filter = st.selectbox("Filter by Status", ["All", "Open", "In Progress", "Resolved", "Closed"])
    params = {} if complaint_filter == "All" else {"status": complaint_filter}

    complaints = api_get("/complaints/all", params=params)
    if complaints:
        for c in complaints:
            priority_icons = {"Low": "🟢", "Medium": "🟡", "High": "🟠", "Critical": "🔴"}
            icon = priority_icons.get(c["priority"], "⚪")

            with st.expander(f"{icon} {c['complaint_ref']} — {c['subject']} [{c['status']}]"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Citizen ID:** {c['citizen_id']}")
                    st.markdown(f"**Priority:** {c['priority']}")
                    st.markdown(f"**Status:** {c['status']}")
                with col2:
                    st.markdown(f"**Created:** {c.get('created_at', 'N/A')}")
                    if c.get("application_id"):
                        st.markdown(f"**Linked App:** #{c['application_id']}")

                st.markdown(f"**Description:** {c['description']}")

                if c["status"] not in ("Resolved", "Closed"):
                    new_status = st.selectbox(
                        "Update Status",
                        ["In Progress", "Resolved", "Closed"],
                        key=f"cmp_status_{c['complaint_id']}",
                    )
                    if st.button("Update", key=f"cmp_update_{c['complaint_id']}"):
                        result = api_put(f"/complaints/{c['complaint_id']}/status", {"status": new_status})
                        if result:
                            st.success(f"Complaint {c['complaint_ref']} updated to '{new_status}'!")
                            st.rerun()
    else:
        st.info("No complaints found.")

# ── Tab 4: Officer Performance ─────────────────────────────────────────────────
with tab4:
    st.subheader("👥 Officer Performance")

    if st.session_state.get("role") == "admin":
        perf = api_get("/admin/officer-performance")
        if perf:
            import pandas as pd
            df = pd.DataFrame(perf)
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Chart
            import plotly.express as px
            fig = px.bar(df, x="officer_name", y=["approved", "rejected"],
                         title="Officer-wise Processing Summary",
                         barmode="group",
                         color_discrete_sequence=["#10b981", "#ef4444"])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No officer data available.")
    else:
        st.info("Officer performance metrics are available to admins only.")
