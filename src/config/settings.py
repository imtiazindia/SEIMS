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
    
    # Try to get from Streamlit secrets first (for Streamlit Cloud)
    try:
        if hasattr(st, 'secrets') and 'secrets' in dir(st):
            database_url = st.secrets.get('DATABASE_URL', None)
            secret_key = st.secrets.get('SECRET_KEY', None)
        else:
            database_url = None
            secret_key = None
    except:
        database_url = None
        secret_key = None
    
    # Fall back to environment variables (for local development)
    if not database_url:
        database_url = os.getenv('DATABASE_URL')
    if not secret_key:
        secret_key = os.getenv('SECRET_KEY')
    
    # Final fallback to defaults (should not be used in production)
    config = {
        'database_url': database_url or 'postgresql://localhost/seims_db',
        'secret_key': secret_key or 'change-this-secret-key',
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

