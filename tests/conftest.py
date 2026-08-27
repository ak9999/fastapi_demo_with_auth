"""Shared test fixtures and configuration."""

import sys
from collections.abc import Generator
from pathlib import Path

import pytest
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Add src to path so imports work correctly
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app.core.database import Base


@pytest.fixture
def faker_instance() -> Faker:
    """Provide a Faker instance for tests."""
    return Faker()


@pytest.fixture
def db_session() -> Generator[Session]:
    """Provide an isolated in-memory SQLite session for each test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = session_local()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()
