"""
Database connection and session management
"""

from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError
from src.config.settings import load_config

# Initialize engine and session factory lazily
_engine = None
_SessionLocal = None
_config = None

def _get_engine():
    """Get or create database engine (lazy initialization)"""
    global _engine, _SessionLocal, _config
    
    if _engine is None:
        # Load config when actually needed (not at import time)
        _config = load_config()
        
        try:
            _engine = create_engine(
                _config['database_url'],
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
                connect_args={
                    "connect_timeout": 10
                }
            )
            # Create session factory
            _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
        except Exception as e:
            _engine = None
            _SessionLocal = None
            print(f"Warning: Could not create database engine: {e}")
    
    return _engine, _SessionLocal

@contextmanager
def get_db_session():
    """Get database session context manager"""
    db_engine, db_session_local = _get_engine()
    
    if db_engine is None or db_session_local is None:
        config = load_config()
        raise ConnectionError(
            f"Database engine not initialized.\n\n"
            f"Current DATABASE_URL: {config.get('database_url', 'Not set')}\n\n"
            f"Please check your DATABASE_URL configuration:\n"
            f"- For Streamlit Cloud: Verify secrets are set correctly\n"
            f"- For local development: Create a .env file with DATABASE_URL\n\n"
            f"See DATABASE_SETUP.md for setup instructions."
        )
    
    session = db_session_local()
    try:
        yield session
        session.commit()
    except OperationalError as e:
        session.rollback()
        error_msg = str(e)
        # Get the actual config to show what URL was used
        config = load_config()
        db_url = config.get('database_url', 'Not set')
        # Mask password in URL for display
        if '@' in db_url and db_url != 'Not set':
            try:
                parts = db_url.split('@')
                if '://' in parts[0]:
                    scheme_user = parts[0].split('://')
                    if ':' in scheme_user[1]:
                        user = scheme_user[1].split(':')[0]
                        display_url = f"{scheme_user[0]}://{user}:***@{'@'.join(parts[1:])}"
                    else:
                        display_url = db_url
                else:
                    display_url = db_url
            except:
                display_url = db_url
        else:
            display_url = db_url
        
        if "Connection refused" in error_msg or "could not connect" in error_msg.lower():
            raise ConnectionError(
                f"❌ Cannot connect to PostgreSQL database.\n\n"
                f"**Current DATABASE_URL:** `{display_url}`\n\n"
                f"**Error:** {error_msg}\n\n"
                f"**Diagnosis:**\n"
                f"- The app is trying to connect to: `{display_url.split('@')[-1] if '@' in display_url else display_url}`\n"
                f"- If this shows 'localhost', your secrets/env vars are not being read correctly\n\n"
                f"**Solutions:**\n"
                f"1. **For Streamlit Cloud:** Verify secrets are set (Settings → Secrets)\n"
                f"2. **For local dev:** Create a `.env` file with `DATABASE_URL=your_connection_string`\n"
                f"3. **Check format:** Make sure no quotes in secrets file values\n"
                f"4. **Restart app:** After changing secrets, restart the app\n\n"
                f"See TROUBLESHOOTING_CONNECTION.md for detailed help."
            ) from e
        raise
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def get_db() -> Session:
    """Get database session (for dependency injection)"""
    db_engine, db_session_local = _get_engine()
    
    if db_engine is None or db_session_local is None:
        config = load_config()
        raise ConnectionError(
            f"Database engine not initialized.\n\n"
            f"Current DATABASE_URL: {config.get('database_url', 'Not set')}\n\n"
            f"Please check your DATABASE_URL configuration:\n"
            f"- For Streamlit Cloud: Verify secrets are set correctly\n"
            f"- For local development: Create a .env file with DATABASE_URL\n\n"
            f"See DATABASE_SETUP.md for setup instructions."
        )
    
    db = db_session_local()
    try:
        yield db
    finally:
        db.close()

