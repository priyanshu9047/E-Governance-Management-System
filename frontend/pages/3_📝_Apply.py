"""
Apply Page — Submit a new application.
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from frontend.utils import api_get, api_post, require_login

st.set_page_config(page_title="Apply | E-Gov Portal", page_icon="📝", layout="wide")

require_login()

st.markdown("# 📝 Apply for a Service")
st.markdown("Select a service, fill in details, and submit your application.")
st.markdown("---")

# Step 1: Select Service
services = api_get("/services/")
if not services:
    st.stop()

service_map = {f"{s['name']} ({s.get('department_name', '')}) — ₹{s['fee']:.2f}": s for s in services}
service_options = list(service_map.keys())
default_index = 0

# Pre-select service if navigating from Services page
if "prefill_service_id" in st.session_state:
    for i, s in enumerate(services):
        if s["service_id"] == st.session_state["prefill_service_id"]:
            default_index = i
            break

selected_name = st.selectbox("🏷️ Select a Service", service_options, index=default_index)
selected_service = service_map[selected_name]

st.markdown("### Service Details")
col1, col2, col3 = st.columns(3)
with col1:
    st.info(f"**Service:** {selected_service['name']}")
with col2:
    st.info(f"**Fee:** ₹{selected_service['fee']:.2f}")
with col3:
    st.info(f"**Processing:** {selected_service['processing_days']} days")

if selected_service.get("description"):
    st.markdown(f"*{selected_service['description']}*")

# Step 2: Show requirements
st.markdown("### 📎 Required Documents")
reqs = api_get(f"/services/{selected_service['service_id']}/requirements")
if reqs:
    for req in reqs:
        mandatory = "🔴 Required" if req["is_mandatory"] else "🟡 Optional"
        st.markdown(f"- **{req['document_name']}** ({mandatory}) — {req.get('description', '')}")
else:
    st.markdown("*No specific documents required.*")

st.markdown("---")

# Step 3: Upload Documents
st.markdown("### 📤 Upload Documents")
uploaded_files = []
num_docs = st.number_input("How many documents to upload?", min_value=0, max_value=10, value=1)

for i in range(num_docs):
    col1, col2 = st.columns([1, 2])
    with col1:
        doc_name = st.text_input(f"Document Name #{i+1}", key=f"doc_name_{i}", placeholder="e.g. Aadhaar Card")
    with col2:
        file = st.file_uploader(f"Upload File #{i+1}", key=f"file_{i}", type=["pdf", "jpg", "jpeg", "png", "doc", "docx"])
    if doc_name and file:
        uploaded_files.append((doc_name, file))

st.markdown("---")

# Step 4: Submit
if st.button("🚀 Submit Application", use_container_width=True, type="primary"):
    with st.spinner("Submitting application..."):
        # Create application
        result = api_post("/applications/", {"service_id": selected_service["service_id"]})

        if result:
            app_ref = result.get("application_ref", "N/A")
            app_id = result.get("application_id")

            # Upload documents
            doc_success = 0
            for doc_name, file in uploaded_files:
                file.seek(0)
                doc_result = api_post(
                    "/documents/upload",
                    data={"application_id": str(app_id), "document_name": doc_name},
                    files={"file": (file.name, file.read(), file.type)},
                )
                if doc_result:
                    doc_success += 1

            st.success(f"""
            ✅ **Application Submitted Successfully!**

            - **Application Ref:** `{app_ref}`
            - **Service:** {selected_service['name']}
            - **Fee:** ₹{selected_service['fee']:.2f}
            - **Documents Uploaded:** {doc_success}/{len(uploaded_files)}

            Please note your reference number for tracking.
            """)

            st.balloons()

            # Prompt payment
            if selected_service["fee"] > 0:
                st.markdown("---")
                st.markdown("### 💳 Make Payment")
                payment_method = st.selectbox(
                    "Payment Method",
                    ["UPI", "Net Banking", "Debit Card", "Credit Card"],
                )
                if st.button("💰 Pay Now", use_container_width=True):
                    pay_result = api_post("/payments/", {
                        "application_id": app_id,
                        "payment_method": payment_method,
                    })
                    if pay_result:
                        st.success(f"✅ Payment of ₹{pay_result['amount']:.2f} completed! Transaction: `{pay_result['transaction_ref']}`")
