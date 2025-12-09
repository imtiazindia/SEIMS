"""
Database connection diagnostics
Runs automatically at app startup to verify database connectivity.

IMPORTANT: This module uses the same configuration loader as the main
application (`src.config.settings.load_config`) so diagnostics and the
app always use the **exact same** DATABASE_URL and settings.
"""

import os
from typing import Tuple, Optional
from dotenv import load_dotenv
from src.config.settings import load_config

# Load environment variables for local development (same as settings.py)
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


def check_database_config() -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Check if DATABASE_URL is configured
    
    Returns:
        (is_configured, display_url, source)
    """
    try:
        # Use the same configuration logic as the main app
        config = load_config()
        database_url = config.get("database_url")
        source = config.get("_config_source", "unknown")
    except Exception:
        database_url = None
        source = "Not configured"

    if not database_url:
        # Check if .env file exists to give a more helpful hint
        if os.path.exists(".env"):
            source = ".env file present but DATABASE_URL missing or unreadable"
        else:
            source = "Not configured (.env missing and no Streamlit secrets)"
        return False, None, source

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

