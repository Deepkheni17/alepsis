"""
Database configuration and session management.
SQLite database with SQLAlchemy ORM.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite database file path
# For production, consider PostgreSQL or MySQL
DATABASE_URL = "sqlite:///./invoices.db"

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Required for SQLite
)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session.
    Ensures session is closed after request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    Creates all tables defined by ORM models.
    """
    Base.metadata.create_all(bind=engine)
