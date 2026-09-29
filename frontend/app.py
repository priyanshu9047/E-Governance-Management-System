"""
E-Governance Service Management System — Streamlit Main App
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ── Page Configuration ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="E-Governance Portal",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main theme */
    .main .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }

    /* Header styling */
    .hero-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }

    .hero-subtitle {
        font-size: 1.1rem;
        color: #9ca3af;
        text-align: center;
        margin-bottom: 2rem;
    }

    /* Card styling — dark mode compatible */
    .stat-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 1px solid #475569;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: transform 0.2s;
    }

    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.4);
    }

    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #e2e8f0;
    }

    .stat-label {
        font-size: 0.9rem;
        color: #94a3b8;
        margin-top: 0.3rem;
    }

    /* Service card — dark mode */
    .service-card {
        background: #1e293b;
        border: 1px solid #475569;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }

    /* Status badge */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }

    .status-submitted { background: #1e3a5f; color: #60a5fa; }
    .status-review { background: #422006; color: #fbbf24; }
    .status-approved { background: #064e3b; color: #34d399; }
    .status-rejected { background: #450a0a; color: #f87171; }

    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 0;
        color: #9ca3af;
        font-size: 0.85rem;
        border-top: 1px solid #374151;
        margin-top: 3rem;
    }

    /* Login form — use Streamlit's native dark styling */
    div[data-testid="stForm"] {
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #374151;
    }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ────────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("### 🏛️ E-Gov Portal")
        st.markdown("---")

        if st.session_state.get("token"):
            st.markdown(f"👤 **{st.session_state.get('full_name', 'User')}**")
            st.markdown(f"🏷️ Role: `{st.session_state.get('role', 'citizen')}`")
            st.markdown("---")

            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.clear()
                st.rerun()
        else:
            st.info("Please login or register to access all features.")

        st.markdown("---")
        st.markdown(
            """
            <div style='text-align: center; color: #9ca3af; font-size: 0.8rem;'>
                E-Governance System v1.0<br>
                © 2024 Digital India
            </div>
            """,
            unsafe_allow_html=True,
        )


render_sidebar()


# ── Main Content ───────────────────────────────────────────────────────────────

st.markdown('<h1 class="hero-title">🏛️ Digital E-Governance Portal</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-subtitle">Apply for government services online — anytime, anywhere</p>',
    unsafe_allow_html=True,
)

# If not logged in, show login/register
if not st.session_state.get("token"):
    from frontend.utils import api_post

    tab_login, tab_register = st.tabs(["🔐 Login", "📝 Register"])

    with tab_login:
        with st.form("login_form"):
            st.subheader("Welcome Back")
            email = st.text_input("Email", placeholder="Enter your email")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Login", use_container_width=True)

            if submitted and email and password:
                result = api_post("/auth/login", {"email": email, "password": password})
                if result:
                    st.session_state["token"] = result["access_token"]
                    st.session_state["user_id"] = result["user_id"]
                    st.session_state["role"] = result["role"]
                    st.session_state["full_name"] = result["full_name"]
                    st.success(f"✅ Welcome, {result['full_name']}!")
                    st.rerun()

    with tab_register:
        with st.form("register_form"):
            st.subheader("Create Account")
            col1, col2 = st.columns(2)
            with col1:
                full_name = st.text_input("Full Name *", placeholder="Your full name")
                email_r = st.text_input("Email *", placeholder="your@email.com")
                password_r = st.text_input("Password *", type="password", placeholder="Min 6 characters")
            with col2:
                phone = st.text_input("Phone", placeholder="10-digit number")
                dob = st.date_input("Date of Birth", value=None)
                aadhaar = st.text_input("Aadhaar Number", placeholder="12-digit number")

            address = st.text_area("Address", placeholder="Your full address")
            submitted_r = st.form_submit_button("Register", use_container_width=True)

            if submitted_r and full_name and email_r and password_r:
                data = {
                    "full_name": full_name,
                    "email": email_r,
                    "password": password_r,
                    "phone": phone or None,
                    "address": address or None,
                    "date_of_birth": str(dob) if dob else None,
                    "aadhaar_number": aadhaar or None,
                }
                result = api_post("/auth/register", data)
                if result:
                    st.session_state["token"] = result["access_token"]
                    st.session_state["user_id"] = result["user_id"]
                    st.session_state["role"] = result["role"]
                    st.session_state["full_name"] = result["full_name"]
                    st.success(f"✅ Registration successful! Welcome, {result['full_name']}!")
                    st.rerun()

else:
    # Dashboard for logged-in users
    from frontend.utils import api_get

    st.markdown("---")

    role = st.session_state.get("role", "citizen")

    if role == "citizen":
        # Citizen Dashboard
        st.subheader(f"👋 Welcome, {st.session_state.get('full_name', 'Citizen')}!")

        apps = api_get("/applications/my")
        if apps is not None:
            col1, col2, col3, col4 = st.columns(4)

            total = len(apps)
            approved = len([a for a in apps if a["status"] == "Approved"])
            pending = len([a for a in apps if a["status"] in ("Submitted", "Under Review")])
            rejected = len([a for a in apps if a["status"] == "Rejected"])

            with col1:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-number">{total}</div>
                    <div class="stat-label">📋 Total Applications</div>
                </div>""", unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-number">{approved}</div>
                    <div class="stat-label">✅ Approved</div>
                </div>""", unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-number">{pending}</div>
                    <div class="stat-label">⏳ Pending</div>
                </div>""", unsafe_allow_html=True)
            with col4:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-number">{rejected}</div>
                    <div class="stat-label">❌ Rejected</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Recent applications table
            if apps:
                st.subheader("📄 Recent Applications")
                import pandas as pd
                df = pd.DataFrame(apps)[["application_ref", "service_name", "department_name", "status", "submitted_at"]]
                df.columns = ["Ref #", "Service", "Department", "Status", "Submitted"]
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No applications yet. Go to **Services** to apply!")

        # Unread notifications
        notif_count = api_get("/notifications/unread/count")
        if notif_count and notif_count.get("unread_count", 0) > 0:
            st.warning(f"🔔 You have {notif_count['unread_count']} unread notification(s).")

    else:
        # Officer/Admin Dashboard
        st.subheader(f"🔧 Officer Dashboard — {st.session_state.get('full_name')}")

        stats = api_get("/admin/stats")
        if stats:
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("Total Applications", stats["total_applications"])
            with col2:
                st.metric("Approved", stats["approved"])
            with col3:
                st.metric("Pending", stats["pending"])
            with col4:
                st.metric("Rejected", stats["rejected"])
            with col5:
                st.metric("Avg Days", stats.get("avg_processing_days", "N/A"))

            st.markdown("---")

            # Recent applications
            recent = api_get("/admin/recent-applications?limit=10")
            if recent:
                st.subheader("📋 Recent Applications")
                import pandas as pd
                df = pd.DataFrame(recent)
                st.dataframe(df, use_container_width=True, hide_index=True)


# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="footer">
        🏛️ Digital E-Governance Service Management System | Built with Streamlit + FastAPI + MySQL<br>
        Designed for SQL Database Project Demonstration
    </div>
    """,
    unsafe_allow_html=True,
)
