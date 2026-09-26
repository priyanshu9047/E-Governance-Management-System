"""
Track Application Page — Check application status with timeline.
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from frontend.utils import api_get, is_logged_in

st.set_page_config(page_title="Track Application | E-Gov Portal", page_icon="🔍", layout="wide")

st.markdown("""
<style>
    .timeline-step {
        display: flex;
        align-items: center;
        padding: 0.8rem 0;
    }
    .timeline-dot {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        margin-right: 12px;
        flex-shrink: 0;
    }
    .dot-done { background: #10b981; color: white; }
    .dot-pending { background: #d1d5db; color: #6b7280; }
    .dot-current { background: #3b82f6; color: white; animation: pulse 2s infinite; }
    @keyframes pulse {
        0%, 100% { box-shadow: 0 0 0 0 rgba(59,130,246,0.4); }
        50% { box-shadow: 0 0 0 8px rgba(59,130,246,0); }
    }
</style>
""", unsafe_allow_html=True)

st.markdown("# 🔍 Track Your Application")
st.markdown("Enter your application reference number to check the current status.")
st.markdown("---")

# Track by reference
app_ref = st.text_input("📋 Application Reference Number", placeholder="e.g., APP10001")

if st.button("🔍 Track", use_container_width=True):
    if not app_ref:
        st.warning("Please enter an application reference number.")
    else:
        result = api_get(f"/applications/track/{app_ref}")
        if result:
            st.markdown("---")

            # Application details
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Application Ref:** `{result['application_ref']}`")
                st.markdown(f"**Service:** {result['service_name']}")
                st.markdown(f"**Department:** {result['department_name']}")
            with col2:
                st.markdown(f"**Current Status:** **{result['status']}**")
                st.markdown(f"**Submitted:** {result.get('submitted_at', 'N/A')}")
                st.markdown(f"**Last Updated:** {result.get('updated_at', 'N/A')}")

            if result.get("remarks"):
                st.warning(f"📝 **Officer Remarks:** {result['remarks']}")

            # Timeline
            st.markdown("### 📊 Application Timeline")

            status_order = ['Submitted', 'Under Review', 'Documents Verified', 'Approved']
            current_status = result['status']

            if current_status == 'Rejected':
                # Special handling for rejected
                for s in ['Submitted', 'Under Review']:
                    st.markdown(f"""
                    <div class="timeline-step">
                        <div class="timeline-dot dot-done">✓</div>
                        <div><strong>{s}</strong></div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown(f"""
                <div class="timeline-step">
                    <div class="timeline-dot" style="background: #ef4444; color: white;">✕</div>
                    <div><strong style="color: #ef4444;">Rejected</strong></div>
                </div>
                """, unsafe_allow_html=True)
            elif current_status == 'Returned':
                for s in ['Submitted']:
                    st.markdown(f"""
                    <div class="timeline-step">
                        <div class="timeline-dot dot-done">✓</div>
                        <div><strong>{s}</strong></div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown(f"""
                <div class="timeline-step">
                    <div class="timeline-dot" style="background: #f59e0b; color: white;">⟲</div>
                    <div><strong style="color: #f59e0b;">Returned — Documents requested</strong></div>
                </div>
                """, unsafe_allow_html=True)
            else:
                current_idx = status_order.index(current_status) if current_status in status_order else -1
                for i, s in enumerate(status_order):
                    if i < current_idx:
                        dot_class = "dot-done"
                        icon = "✓"
                    elif i == current_idx:
                        dot_class = "dot-current"
                        icon = "●"
                    else:
                        dot_class = "dot-pending"
                        icon = "○"

                    st.markdown(f"""
                    <div class="timeline-step">
                        <div class="timeline-dot {dot_class}">{icon}</div>
                        <div><strong>{s}</strong></div>
                    </div>
                    """, unsafe_allow_html=True)

st.markdown("---")

# If logged in, show all their applications
if is_logged_in():
    st.markdown("### 📋 All Your Applications")
    apps = api_get("/applications/my")
    if apps:
        import pandas as pd
        df = pd.DataFrame(apps)[["application_ref", "service_name", "department_name", "status", "submitted_at", "remarks"]]
        df.columns = ["Ref #", "Service", "Department", "Status", "Submitted", "Remarks"]

        # Color status
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("You don't have any applications yet.")
