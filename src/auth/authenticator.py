"""
Authentication and authorization functions
"""

import streamlit as st
from src.database.connection import get_db_session
from src.database.models import User
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def authenticate_user(email: str, password: str) -> dict:
    """
    Authenticate a user by email and password
    
    Returns:
        dict: User information if authenticated, None otherwise
    """
    try:
        with get_db_session() as session:
            user = session.query(User).filter(User.email == email).first()
            
            if user and verify_password(password, user.password_hash):
                return {
                    'user_id': user.user_id,
                    'email': user.email,
                    'role': user.role,
                    'name': user.name
                }
            return None
    except Exception as e:
        st.error(f"Authentication error: {str(e)}")
        return None

def check_authentication():
    """Check if user is authenticated"""
    return st.session_state.get('authenticated', False)

def require_role(*allowed_roles):
    """Decorator to require specific roles"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not check_authentication():
                st.error("Please log in to access this page.")
                st.stop()
            
            user_role = st.session_state.get('user_role')
            if user_role not in allowed_roles:
                st.error("You do not have permission to access this page.")
                st.stop()
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

