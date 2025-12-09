"""
Application configuration and settings
"""

import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables (for local development)
load_dotenv()

def load_config():
    """Load application configuration from environment variables or Streamlit secrets"""
    
    database_url = None
    secret_key = None
    source = "none"
    
    # Try to get from Streamlit secrets first (for Streamlit Cloud)
    try:
        # Check if we're in a Streamlit context and secrets are available
        if hasattr(st, 'secrets'):
            try:
                # Try different ways to access secrets (Streamlit versions vary)
                secrets_dict = None
                
                # Method 1: Direct access as dict
                if isinstance(st.secrets, dict):
                    secrets_dict = st.secrets
                # Method 2: Access via get method
                elif hasattr(st.secrets, 'get'):
                    # Try to get all secrets to see structure
                    try:
                        if 'DATABASE_URL' in st.secrets:
                            database_url = st.secrets['DATABASE_URL']
                            source = "streamlit_secrets"
                    except:
                        pass
                # Method 3: Try accessing as attribute
                if not database_url:
                    try:
                        if hasattr(st.secrets, 'DATABASE_URL'):
                            database_url = getattr(st.secrets, 'DATABASE_URL')
                            source = "streamlit_secrets"
                    except:
                        pass
                        
                # Also try SECRET_KEY
                if not secret_key:
                    try:
                        if 'SECRET_KEY' in st.secrets:
                            secret_key = st.secrets['SECRET_KEY']
                        elif hasattr(st.secrets, 'SECRET_KEY'):
                            secret_key = getattr(st.secrets, 'SECRET_KEY')
                    except:
                        pass
            except (AttributeError, KeyError, TypeError, RuntimeError) as e:
                # Secrets might not be available yet or in wrong format
                pass
    except (RuntimeError, AttributeError):
        # Not in Streamlit context (e.g., during import or testing)
        pass
    
    # Fall back to environment variables (for local development)
    if not database_url:
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            source = "environment_variable"
    if not secret_key:
        secret_key = os.getenv('SECRET_KEY')
    
    # Final fallback to defaults (should not be used in production)
    # Only use localhost default if we're definitely in a local dev context
    if not database_url:
        # Check if we're running locally (not on Streamlit Cloud)
        is_local = os.getenv('STREAMLIT_SERVER_PORT') is None and 'streamlit' not in str(st.__file__).lower() if hasattr(st, '__file__') else True
        if is_local:
            database_url = 'postgresql://localhost/seims_db'
            source = "default_localhost"
        else:
            # On Streamlit Cloud but no secrets found - this is an error
            database_url = 'postgresql://localhost/seims_db'  # Will fail, but shows the issue
    
    config = {
        'database_url': database_url,
        'secret_key': secret_key or 'change-this-secret-key',
        '_config_source': source,  # Debug info
        'debug': os.getenv('DEBUG', 'False').lower() == 'true',
        'log_level': os.getenv('LOG_LEVEL', 'INFO'),
        
        # AWS S3 Configuration (optional)
        'aws_access_key_id': os.getenv('AWS_ACCESS_KEY_ID'),
        'aws_secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
        'aws_s3_bucket': os.getenv('AWS_S3_BUCKET', 'seims-files'),
        'aws_region': os.getenv('AWS_REGION', 'us-east-1'),
        
        # Email Configuration (optional)
        'email_api_key': os.getenv('EMAIL_API_KEY'),
        'email_from': os.getenv('EMAIL_FROM', 'noreply@seims.edu'),
        
        # SMS Configuration (optional)
        'sms_api_key': os.getenv('SMS_API_KEY'),
        'sms_from': os.getenv('SMS_FROM'),
    }
    
    return config

