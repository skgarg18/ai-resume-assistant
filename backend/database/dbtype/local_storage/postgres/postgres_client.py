"""
PostgreSQL Database Configuration

This module configures the SQLAlchemy engine and session factory used
to interact with the PostgreSQL database.

All repositories should use a SQLAlchemy Session obtained through
the `get_db()` dependency.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# Load environment variables from .env
load_dotenv()

# Construct the PostgreSQL connection URL
DATABASE_URL = (
    f"postgresql+psycopg://"
    f"{os.getenv('DB_USER')}:"
    f"{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:"
    f"{os.getenv('DB_PORT')}/"
    f"{os.getenv('DB_NAME')}"
)

# Create the SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    echo=False,          # Set True to log SQL queries during development
    pool_pre_ping=True,  # Automatically checks if pooled connections are alive
)

# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db():
    """
    FastAPI dependency that provides a database session.

    A new SQLAlchemy session is created for each request and
    automatically closed after the request is completed.

    Usage:
        db: Session = Depends(get_db)
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()