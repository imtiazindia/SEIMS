"""
Application configuration and settings
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def load_config():
    """Load application configuration from environment variables"""
    
    config = {
        'database_url': os.getenv('DATABASE_URL', 'postgresql://localhost/seims_db'),
        'secret_key': os.getenv('SECRET_KEY', 'change-this-secret-key'),
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

