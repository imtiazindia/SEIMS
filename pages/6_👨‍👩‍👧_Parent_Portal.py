"""
Parent Portal page
"""

import streamlit as st

st.set_page_config(page_title="Parent Portal", page_icon="👨‍👩‍👧", layout="wide")

if not st.session_state.get('authenticated'):
    st.error("Please log in to access this page.")
    st.stop()

user_role = st.session_state.get('user_role')

# Check permissions
if user_role != 'parent':
    st.error("You do not have permission to access this page.")
    st.stop()

st.title("👨‍👩‍👧 Parent Portal")

st.info("Parent Portal - View your child's progress and communicate with teachers coming soon")

# Placeholder for parent portal features
tab1, tab2, tab3, tab4 = st.tabs(["Child's Progress", "Assignments", "Messages", "Resources"])

with tab1:
    st.subheader("Child's Progress")
    st.write("View your child's IEP goals and progress will be displayed here.")

with tab2:
    st.subheader("Assignments")
    st.write("View and submit assignments will be implemented here.")

with tab3:
    st.subheader("Messages")
    st.write("Secure messaging with teachers will be implemented here.")

with tab4:
    st.subheader("Resources")
    st.write("Resource library and guides will be available here.")

