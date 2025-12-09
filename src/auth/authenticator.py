"""
Authentication and authorization functions
"""

import streamlit as st
from src.database.connection import get_db_session
from src.database.models import User
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

_BCRYPT_MAX_LENGTH = 72


def _normalize_password(password: str) -> str:
    """
    Normalize password input for bcrypt.

    Bcrypt only uses the first 72 bytes of a password. To avoid runtime
    errors like:
        "password cannot be longer than 72 bytes, truncate manually..."
    we explicitly truncate any longer passwords before hashing/verifying.
    """
    if password is None:
        return password
    return password[:_BCRYPT_MAX_LENGTH]


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash (with safe truncation)."""
    return pwd_context.verify(_normalize_password(plain_password), hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password (with safe truncation)."""
    return pwd_context.hash(_normalize_password(password))

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
    except ConnectionError as e:
        st.error(f"Database Connection Error\n\n{str(e)}\n\nPlease check TROUBLESHOOTING_CONNECTION.md for help.")
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

