"""
Login page for SEIMS
"""

import streamlit as st
from src.auth.authenticator import authenticate_user

def show_login_page():
    """Display login page"""
    
    st.title("🎓 SEIMS Login")
    st.markdown("### Special Education IEP Management System")
    
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="your.email@example.com")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submit_button = st.form_submit_button("Login", use_container_width=True)
        
        if submit_button:
            if not email or not password:
                st.error("Please enter both email and password.")
            else:
                user = authenticate_user(email, password)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.user_id = user['user_id']
                    st.session_state.user_role = user['role']
                    st.session_state.user_name = user['name']
                    st.session_state.user_email = user['email']
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid email or password. Please try again.")
    
    st.markdown("---")
    st.caption("Contact your administrator if you need access to the system.")

