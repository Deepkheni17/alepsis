"""
Database configuration and session management.
Production PostgreSQL with SQLAlchemy ORM.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment (required for production)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create SQLAlchemy engine with production settings
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,          # Verify connections before using
    pool_size=5,                  # Max 5 concurrent connections
    max_overflow=10,              # Allow 10 additional connections if needed
    pool_recycle=3600,            # Recycle connections after 1 hour
    echo=False,                   # Disable SQL logging in production
    future=True                   # Use SQLAlchemy 2.0 style
)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False        # Keep objects usable after commit
)

# Base class for ORM models
Base = declarative_base()


def get_db():
    """
    FastAPI dependency for database sessions.
    Automatically handles session lifecycle and cleanup.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables from ORM models.
    Use Alembic migrations for production instead.
    """
    Base.metadata.create_all(bind=engine)
