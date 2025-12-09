"""
Database connection and session management
"""

from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.config.settings import load_config

config = load_config()

# Create database engine
engine = create_engine(
    config['database_url'],
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_db_session():
    """Get database session context manager"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def get_db() -> Session:
    """Get database session (for dependency injection)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

