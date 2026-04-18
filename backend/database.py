"""
Database configuration with PostgreSQL production support.

Features:
- PostgreSQL for production (Render, Supabase, AWS RDS, etc.)
- SQLite fallback for development
- Connection pooling for high-traffic 24/7 bots
- Automatic reconnection on connection loss
- WAL mode for SQLite performance
"""
import logging
import sqlalchemy
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError
from sqlalchemy.pool import QueuePool
from config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# Determine database type
IS_SQLITE = "sqlite" in settings.DATABASE_URL

# Connection arguments
connect_args = {}
if IS_SQLITE:
    connect_args = {"check_same_thread": False}
    logger.info(f"Using SQLite database: {settings.DATABASE_URL.split(':///')[1]}")
else:
    logger.info(f"Using PostgreSQL database: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'configured'}")

# Engine configuration for production reliability
try:
    if IS_SQLITE:
        # SQLite configuration
        engine = create_engine(
            settings.DATABASE_URL,
            connect_args=connect_args,
            echo=settings.DEBUG,
            pool_pre_ping=True,  # Enable connection health checks
        )
    else:
        # PostgreSQL configuration with connection pooling for 24/7 bots
        engine = create_engine(
            settings.DATABASE_URL,
            poolclass=QueuePool,
            pool_size=20,  # Number of connections to keep in pool
            max_overflow=40,  # Extra connections allowed during peak
            pool_timeout=30,  # Seconds to wait for available connection
            pool_recycle=1800,  # Recycle connections every 30 min (prevent stale connections)
            pool_pre_ping=True,  # Verify connection before use
            connect_args=connect_args,
            echo=settings.DEBUG,
        )

    # Test connection
    with engine.connect() as conn:
        conn.execute(sqlalchemy.text("SELECT 1"))
    logger.info("Database connection established successfully")

except Exception as e:
    logger.error(f"Database connection failed: {e}")
    logger.warning("Falling back to in-memory SQLite for development")
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )

# Enable foreign keys for SQLite
if IS_SQLITE:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging for better performance
        cursor.close()
    logger.info("SQLite WAL mode enabled for better performance")

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """
    Database session dependency injection.
    Yields session and ensures cleanup after request.
    """
    db = SessionLocal()
    try:
        yield db
    except OperationalError as e:
        logger.error(f"Database operational error: {e}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    Call this on application startup.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        return False
