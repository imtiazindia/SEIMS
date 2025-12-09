"""
Dashboard page - Role-specific dashboard
"""

import streamlit as st
from src.auth.permissions import get_role_display_name

st.set_page_config(page_title="Dashboard", page_icon="🏠", layout="wide")

if not st.session_state.get('authenticated'):
    st.error("Please log in to access this page.")
    st.stop()

user_role = st.session_state.get('user_role')
user_name = st.session_state.get('user_name', 'User')

st.title(f"🏠 Dashboard")
st.markdown(f"### Welcome, {user_name}")
st.caption(f"Role: {get_role_display_name(user_role)}")

# Role-specific dashboard content
if user_role == 'admin':
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Users", "0")
    with col2:
        st.metric("Active Students", "0")
    with col3:
        st.metric("Active IEPs", "0")
    with col4:
        st.metric("Pending Tasks", "0")
    
    st.info("Admin dashboard - Full system overview coming soon")

elif user_role == 'special_educator':
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("My Students", "0")
    with col2:
        st.metric("IEPs to Review", "0")
    with col3:
        st.metric("Upcoming Assessments", "0")
    
    st.info("Special Educator dashboard - Student and IEP management coming soon")

elif user_role == 'teacher' or user_role == 'therapist':
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Today's Sessions", "0")
    with col2:
        st.metric("Assigned Students", "0")
    with col3:
        st.metric("Pending Logs", "0")
    
    st.info("Teacher/Therapist dashboard - Session management coming soon")

elif user_role == 'parent':
    st.info("Parent dashboard - View your child's progress coming soon")

else:
    st.info("Dashboard content for your role is being developed.")

