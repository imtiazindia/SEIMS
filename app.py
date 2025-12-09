"""
SEIMS - Special Education IEP Management System
Main Streamlit Application Entry Point
"""

import streamlit as st
from src.config.settings import load_config
from src.auth.authenticator import check_authentication
from src.utils.diagnostics import run_diagnostics

# Page configuration
st.set_page_config(
    page_title="SEIMS - Special Education IEP Management System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Run database diagnostics before anything else and cache result in session
if "db_diagnostics" not in st.session_state:
    st.session_state.db_diagnostics = run_diagnostics()

diagnostics = st.session_state.db_diagnostics

with st.container():
    if diagnostics["config_ok"] and diagnostics["connection_ok"]:
        # Explicit confirmation banner before showing login / app
        st.success(
            "✅ Database connection successful. Connected to Supabase Session Pooler."
        )
        st.caption(
            f"Source: {diagnostics['config_source']} · "
            f"DATABASE_URL: `{diagnostics['database_url']}`"
        )
    else:
        st.error("⚠️ Database Connection Issue Detected")

        if not diagnostics["config_ok"]:
            st.error(f"**Configuration Error:** {diagnostics['message']}")
            st.info(f"**Source:** {diagnostics['config_source']}")
            st.markdown(
                """
                **To fix this:**
                - **For local development:** Create a `.env` file with `DATABASE_URL=your_connection_string`
                - **For Streamlit Cloud:** Go to Settings → Secrets and add `DATABASE_URL`
                - See `STREAMLIT_CLOUD_SECRETS_UPDATE.md` for detailed instructions
                """
            )
        else:
            st.error(f"**Connection Error:** {diagnostics['message']}")
            if diagnostics.get("details"):
                st.code(diagnostics["details"], language=None)

            if diagnostics.get("database_url"):
                st.info(f"**DATABASE_URL:** `{diagnostics['database_url']}`")
            if diagnostics.get("config_source"):
                st.info(f"**Config Source:** {diagnostics['config_source']}")

            st.markdown(
                """
                **Troubleshooting:**
                1. Verify your DATABASE_URL is correct
                2. Check if your Supabase project is active (not paused)
                3. Ensure you're using the Session Pooler connection string for IPv4 networks
                4. See `TROUBLESHOOTING_CONNECTION.md` for more help
                """
            )

        with st.expander("🔍 View Full Diagnostics", expanded=False):
            st.json(diagnostics)

        st.warning(
            "⚠️ The app may not function correctly without a database connection."
        )

    st.divider()

# Load configuration
config = load_config()

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "user_id" not in st.session_state:
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

