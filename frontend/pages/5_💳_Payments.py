"""
Payments Page — View and make payments.
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from frontend.utils import api_get, api_post, require_login

st.set_page_config(page_title="Payments | E-Gov Portal", page_icon="💳", layout="wide")

require_login()

st.markdown("# 💳 Payments")
st.markdown("View your payment history and make pending payments.")
st.markdown("---")

# Payment History
st.subheader("📜 Payment History")
payments = api_get("/payments/my")

if payments:
    import pandas as pd
    df = pd.DataFrame(payments)[["payment_id", "application_id", "amount", "payment_method", "transaction_ref", "status", "paid_at"]]
    df.columns = ["ID", "Application", "Amount (₹)", "Method", "Transaction Ref", "Status", "Date"]
    st.dataframe(df, use_container_width=True, hide_index=True)

    total_paid = sum(p["amount"] for p in payments if p["status"] == "Completed")
    st.success(f"💰 Total Paid: **₹{total_paid:,.2f}**")
else:
    st.info("No payment records found.")

st.markdown("---")

# Make a new payment
st.subheader("💰 Make a Payment")
st.markdown("Pay the fee for an application.")

apps = api_get("/applications/my")
if apps:
    unpaid_apps = []
    for app in apps:
        # Check if this app already has a completed payment
        app_payments = api_get(f"/payments/application/{app['application_id']}")
        has_paid = any(p["status"] == "Completed" for p in (app_payments or []))
        if not has_paid:
            unpaid_apps.append(app)

    if unpaid_apps:
        app_map = {f"{a['application_ref']} — {a.get('service_name', 'N/A')}": a for a in unpaid_apps}
        selected = st.selectbox("Select Application", list(app_map.keys()))
        selected_app = app_map[selected]

        payment_method = st.selectbox("Payment Method", ["UPI", "Net Banking", "Debit Card", "Credit Card"])

        if st.button("💳 Process Payment", use_container_width=True, type="primary"):
            result = api_post("/payments/", {
                "application_id": selected_app["application_id"],
                "payment_method": payment_method,
            })
            if result:
                st.success(f"""
                ✅ **Payment Successful!**
                - Amount: ₹{result['amount']:.2f}
                - Transaction: `{result['transaction_ref']}`
                - Method: {result['payment_method']}
                """)
                st.balloons()
                st.rerun()
    else:
        st.info("All applications have been paid for. ✅")
