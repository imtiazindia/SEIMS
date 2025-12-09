"""
Database connection diagnostics
Runs automatically at app startup to verify database connectivity
"""

import os
from typing import Tuple, Optional
from dotenv import load_dotenv

# Load environment variables for local development
load_dotenv()


def mask_password_in_url(url: str) -> str:
    """Mask password in database URL for display"""
    if not url or '@' not in url:
        return url
    
    try:
        parts = url.split('@')
        if '://' in parts[0]:
            scheme_user = parts[0].split('://')
            if ':' in scheme_user[1]:
                user = scheme_user[1].split(':')[0]
                display_url = f"{scheme_user[0]}://{user}:***@{'@'.join(parts[1:])}"
                return display_url
    except:
        pass
    
    return url


def check_database_config() -> Tuple[bool, str, Optional[str]]:
    """
    Check if DATABASE_URL is configured
    
    Returns:
        (is_configured, display_url, source)
    """
    database_url = os.getenv('DATABASE_URL')
    source = None
    
    # Try to get from Streamlit secrets (for Streamlit Cloud)
    try:
        import streamlit as st
        if hasattr(st, 'secrets'):
            try:
                if isinstance(st.secrets, dict) and 'DATABASE_URL' in st.secrets:
                    database_url = st.secrets['DATABASE_URL']
                    source = "Streamlit Cloud Secrets"
                elif hasattr(st.secrets, 'DATABASE_URL'):
                    database_url = getattr(st.secrets, 'DATABASE_URL')
                    source = "Streamlit Cloud Secrets"
            except:
                pass
    except:
        pass
    
    if not database_url:
        # Check if .env file exists
        if os.path.exists('.env'):
            source = ".env file (but DATABASE_URL not found)"
        else:
            source = "Not configured"
        return False, None, source
    
    if not source:
        source = ".env file" if os.path.exists('.env') else "Environment variable"
    
    display_url = mask_password_in_url(database_url)
    return True, display_url, source


def test_database_connection() -> Tuple[bool, str, Optional[str]]:
    """
    Test database connection
    
    Returns:
        (success, message, details)
    """
    try:
        from src.database.connection import get_db_session, _get_engine
        from sqlalchemy import text
        
        # Check if engine can be initialized
        db_engine, _ = _get_engine()
        if db_engine is None:
            return False, "Database engine not initialized", None
        
        # Test connection
        with get_db_session() as session:
            # Test query
            result = session.execute(text("SELECT version();"))
            version = result.scalar()
            version_info = version.split(',')[0] if version else "Unknown"
            
            # Check if tables exist
            result = session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                LIMIT 5;
            """))
            tables = [row[0] for row in result]
            
            details = f"PostgreSQL version: {version_info}"
            if tables:
                details += f"\nFound {len(tables)} table(s): {', '.join(tables)}"
            else:
                details += "\n⚠ No tables found - you may need to run database migrations"
            
            return True, "Connection successful", details
            
    except ImportError as e:
        return False, f"Could not import database modules: {e}", None
    except ConnectionError as e:
        return False, "Connection failed", str(e)
    except Exception as e:
        return False, f"Error: {type(e).__name__}", str(e)


def run_diagnostics() -> dict:
    """
    Run complete database diagnostics
    
    Returns:
        Dictionary with diagnostic results
    """
    results = {
        'config_ok': False,
        'connection_ok': False,
        'database_url': None,
        'config_source': None,
        'message': None,
        'details': None
    }
    
    # Check configuration
    config_ok, display_url, source = check_database_config()
    results['config_ok'] = config_ok
    results['database_url'] = display_url
    results['config_source'] = source
    
    if not config_ok:
        results['message'] = "DATABASE_URL not configured"
        return results
    
    # Test connection
    connection_ok, message, details = test_database_connection()
    results['connection_ok'] = connection_ok
    results['message'] = message
    results['details'] = details
    
    return results

