"""
Database configuration and session management.
Production PostgreSQL with SQLAlchemy ORM.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

# Get database URL from environment (required for production)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# PROACTIVE FIX: Check if we're connecting to Supabase on port 5432
# Railway and some other providers have trouble with IPv6 on port 5432.
# Switch to port 6543 (Supabase Pooler) which usually supports IPv4.
if "supabase.co" in DATABASE_URL and ":5432/" in DATABASE_URL:
    print("Detected Supabase connection on port 5432. Upgrading to port 6543 for IPv4 compatibility.")
    DATABASE_URL = DATABASE_URL.replace(":5432/", ":6543/")

# Ensure sslmode=require if it's not already there for Supabase
if "supabase.co" in DATABASE_URL and "sslmode=" not in DATABASE_URL:
    separator = "&" if "?" in DATABASE_URL else "?"
    DATABASE_URL = f"{DATABASE_URL}{separator}sslmode=require"

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
