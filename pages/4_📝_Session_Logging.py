"""
Session Logging page
"""

import streamlit as st

st.set_page_config(page_title="Session Logging", page_icon="📝", layout="wide")

if not st.session_state.get('authenticated'):
    st.error("Please log in to access this page.")
    st.stop()

user_role = st.session_state.get('user_role')

# Check permissions
if user_role not in ['admin', 'teacher', 'therapist']:
    st.error("You do not have permission to access this page.")
    st.stop()

st.title("📝 Session Logging")

st.info("Session Logging module - Log teaching sessions and track progress coming soon")

# Placeholder for session logging features
tab1, tab2, tab3 = st.tabs(["Today's Sessions", "Log New Session", "Session History"])

with tab1:
    st.subheader("Today's Sessions")
    st.write("Today's session schedule will be displayed here.")

with tab2:
    st.subheader("Log New Session")
    st.write("Session logging form will be implemented here.")

with tab3:
    st.subheader("Session History")
    st.write("Historical session logs will be displayed here.")

