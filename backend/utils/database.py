"""Database connection utilities"""
import os
import sys
import sqlite3
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Load .env file if it exists
try:
    from dotenv import load_dotenv
    env_path = project_root / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # python-dotenv not installed, that's okay

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm import declarative_base

# Try PostgreSQL, fallback to SQLite
try:
    import psycopg2
    USE_POSTGRES = True
except ImportError:
    USE_POSTGRES = False

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///feed.db')

# Log database configuration (safely, in case logging isn't configured yet)
try:
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"DATABASE_URL is set: {bool(DATABASE_URL)}")
    logger.info(f"DATABASE_URL starts with: {DATABASE_URL[:20] if DATABASE_URL else 'None'}...")
    logger.info(f"USE_POSTGRES: {USE_POSTGRES}")
    logger.info(f"Will use PostgreSQL: {USE_POSTGRES and DATABASE_URL and not DATABASE_URL.startswith('sqlite')}")
except Exception:
    pass  # Logging not configured yet, that's okay

# For SQLite, use file path
if DATABASE_URL.startswith('sqlite'):
    try:
        logger.info("Using SQLite database")
    except:
        pass
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # PostgreSQL
    try:
        logger.info("Using PostgreSQL database")
        # Hide password in log
        safe_url = DATABASE_URL
        if '@' in DATABASE_URL:
            parts = DATABASE_URL.split('@')
            if len(parts) == 2:
                safe_url = parts[0].split('//')[0] + '//***@' + parts[1]
        logger.info(f"PostgreSQL connection string: {safe_url}")
    except:
        pass
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Session:
    """Dependency for FastAPI to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_raw_connection():
    """Get raw database connection for worker (non-SQLAlchemy)"""
    if USE_POSTGRES and DATABASE_URL and not DATABASE_URL.startswith('sqlite'):
        return psycopg2.connect(DATABASE_URL)
    else:
        return sqlite3.connect('feed.db')

