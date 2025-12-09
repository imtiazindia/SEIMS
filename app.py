"""
SEIMS - Special Education IEP Management System
Main Streamlit Application Entry Point
"""

import streamlit as st
from src.config.settings import load_config
from src.auth.authenticator import check_authentication

# Page configuration
st.set_page_config(
    page_title="SEIMS - Special Education IEP Management System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load configuration
config = load_config()

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

def main():
    """Main application entry point"""
    
    # Check authentication
    if not st.session_state.authenticated:
        # Show login page
        from pages.login import show_login_page
        show_login_page()
    else:
        # Show main application
        show_main_app()

def show_main_app():
    """Display the main application based on user role"""
    
    # Sidebar navigation
    with st.sidebar:
        st.title("🎓 SEIMS")
        st.write(f"Welcome, {st.session_state.get('user_name', 'User')}")
        st.write(f"Role: {st.session_state.user_role}")
        
        # Navigation menu based on role
        if st.button("🏠 Dashboard"):
            st.switch_page("pages/1_🏠_Dashboard.py")
        
        if st.session_state.user_role in ['admin', 'special_educator', 'junior_staff']:
            if st.button("👥 Student Management"):
                st.switch_page("pages/2_👥_Student_Management.py")
        
        if st.session_state.user_role in ['admin', 'special_educator']:
            if st.button("📋 IEP Management"):
                st.switch_page("pages/3_📋_IEP_Management.py")
        
        if st.session_state.user_role in ['admin', 'teacher', 'therapist']:
            if st.button("📝 Session Logging"):
                st.switch_page("pages/4_📝_Session_Logging.py")
        
        if st.session_state.user_role in ['admin', 'special_educator']:
            if st.button("📊 Assessment & Reporting"):
                st.switch_page("pages/5_📊_Assessment_Reporting.py")
        
        if st.session_state.user_role == 'parent':
            if st.button("👨‍👩‍👧 Parent Portal"):
                st.switch_page("pages/6_👨‍👩‍👧_Parent_Portal.py")
        
        if st.session_state.user_role == 'admin':
            if st.button("⚙️ Admin Panel"):
                st.switch_page("pages/7_⚙️_Admin_Panel.py")
        
        st.divider()
        
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.user_role = None
            st.session_state.user_id = None
            st.rerun()
    
    # Main content area
    st.title("Welcome to SEIMS")
    st.markdown("### Special Education IEP Management System")
    
    st.info("""
    **Select a page from the sidebar to get started.**
    
    - **Dashboard:** View your personalized dashboard
    - **Student Management:** Manage student profiles and registrations
    - **IEP Management:** Create and manage Individualized Education Programs
    - **Session Logging:** Log teaching sessions and track progress
    - **Assessment & Reporting:** Conduct assessments and generate reports
    - **Parent Portal:** Access parent-specific features
    - **Admin Panel:** System administration (Admin only)
    """)

if __name__ == "__main__":
    main()

