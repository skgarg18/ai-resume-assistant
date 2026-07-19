"""
Base class for all SQLAlchemy ORM models.

Every ORM model in the application should inherit from this Base class.
SQLAlchemy uses it to keep track of all mapped models and their metadata.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    """
    pass