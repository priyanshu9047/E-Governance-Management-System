"""
Notifications Page — View and manage notifications.
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from frontend.utils import api_get, api_put, require_login

st.set_page_config(page_title="Notifications | E-Gov Portal", page_icon="📢", layout="wide")

require_login()

st.markdown("# 📢 Notifications")
st.markdown("Stay updated on your application progress.")
st.markdown("---")

# Mark all as read button
col1, col2 = st.columns([3, 1])
with col2:
    if st.button("✅ Mark All Read", use_container_width=True):
        api_put("/notifications/read-all")
        st.rerun()

# Fetch notifications
notifications = api_get("/notifications/")

if notifications:
    unread = [n for n in notifications if not n["is_read"]]
    read = [n for n in notifications if n["is_read"]]

    if unread:
        st.subheader(f"🔔 Unread ({len(unread)})")
        for notif in unread:
            type_icons = {"Info": "ℹ️", "Success": "✅", "Warning": "⚠️", "Error": "❌"}
            icon = type_icons.get(notif["type"], "📌")

            with st.container():
                col1, col2, col3 = st.columns([0.5, 8, 1.5])
                with col1:
                    st.markdown(f"### {icon}")
                with col2:
                    st.markdown(f"**{notif['title']}**")
                    st.markdown(notif["message"])
                    st.caption(f"🕐 {notif.get('created_at', 'N/A')}")
                with col3:
                    if st.button("Mark Read", key=f"read_{notif['notification_id']}"):
                        api_put(f"/notifications/{notif['notification_id']}/read")
                        st.rerun()
                st.markdown("---")

    if read:
        with st.expander(f"📬 Read Notifications ({len(read)})"):
            for notif in read:
                type_icons = {"Info": "ℹ️", "Success": "✅", "Warning": "⚠️", "Error": "❌"}
                icon = type_icons.get(notif["type"], "📌")
                st.markdown(f"{icon} **{notif['title']}** — {notif['message']}")
                st.caption(f"🕐 {notif.get('created_at', 'N/A')}")
                st.markdown("---")
else:
    st.info("📭 No notifications yet.")
