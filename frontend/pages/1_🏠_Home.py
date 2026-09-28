"""
Home Page — Landing and information page.
"""

import streamlit as st

st.set_page_config(page_title="Home | E-Gov Portal", page_icon="🏠", layout="wide")

st.markdown("""
<style>
    .feature-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 1px solid #475569;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        min-height: 180px;
    }
    .feature-icon { font-size: 2.5rem; margin-bottom: 0.5rem; }
    .feature-title { font-size: 1.1rem; font-weight: 600; color: #e2e8f0; }
    .feature-desc { font-size: 0.9rem; color: #94a3b8; margin-top: 0.5rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("# 🏠 Welcome to the E-Governance Portal")
st.markdown("### Your one-stop digital platform for government services")

st.markdown("---")

st.markdown("## 🌟 Features")

col1, col2, col3, col4 = st.columns(4)

features = [
    ("📋", "Apply Online", "Apply for certificates, licenses, and permits from home"),
    ("🔍", "Track Status", "Real-time tracking of your application status"),
    ("💳", "Online Payments", "Secure digital payment for government fees"),
    ("📢", "Notifications", "Instant updates on your application progress"),
    ("🗣️", "Raise Complaints", "File and track complaints easily"),
    ("📊", "Analytics", "Department-wise reports and performance metrics"),
    ("🔒", "Secure & Private", "JWT-based authentication with encrypted passwords"),
    ("⚡", "Fast Processing", "Streamlined digital workflow for quick processing"),
]

for i, (icon, title, desc) in enumerate(features):
    col = [col1, col2, col3, col4][i % 4]
    with col:
        st.markdown(f"""
        <div class="feature-card">
            <div class="feature-icon">{icon}</div>
            <div class="feature-title">{title}</div>
            <div class="feature-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

st.markdown("---")

st.markdown("## 📖 How It Works")

st.markdown("""
1. **Register / Login** — Create your citizen account or login
2. **Browse Services** — Explore available government services
3. **Apply** — Select a service, fill details, upload documents
4. **Pay Fees** — Complete the payment online
5. **Track** — Monitor your application in real-time
6. **Get Certificate** — Receive approval and your certificate
""")

st.markdown("---")

st.markdown("## 🏢 Departments")
st.markdown("""
| Department | Services |
|------------|----------|
| Revenue Department | Income Certificate, Domicile Certificate, Land Records |
| Health Department | Birth Certificate, Death Certificate |
| Education Department | Education Verification, Scholarships |
| Home Department | Police Verification, Character Certificate |
| Urban Development | Trade License, Building Permit |
| Social Welfare | Caste Certificate, Disability Certificate, Senior Citizen ID |
| Transport Department | Driving License, Vehicle Registration |
""")

st.markdown("---")

st.info("💡 **Demo Credentials**: Use `rahul@example.com` / `password123` to login as a citizen, or `suresh@gov.in` / `password123` for officer access.")
