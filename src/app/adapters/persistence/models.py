"""SQLAlchemy ORM models for database persistence."""

from sqlalchemy import Column, Integer, String

from app.core.database import Base


class PersonModel(Base):
    """SQLAlchemy ORM model for the Person table.

    This is the database schema. It maps to the Person domain entity.
    """

    __tablename__ = "persons"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(200), nullable=False)
    last_name = Column(String(200), nullable=False)
    age = Column(Integer, nullable=False)
    hometown = Column(String(200), nullable=False)
