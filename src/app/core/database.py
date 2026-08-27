"""Database configuration and session management."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.core.config import settings

# Create the SQLAlchemy engine
# - echo=False: don't log SQL queries (set to True for debugging)
# - check_same_thread=False: allows SQLite to be used with threads (FastAPI requirement)
#   only needed for SQLite; harmless to pass for other DBs during local dev
engine = create_engine(
    settings.database_url,
    echo=False,
    connect_args={"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {},
)

# SessionLocal creates new database sessions
# Each request will get its own session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class that all ORM models inherit from
Base = declarative_base()


def get_db() -> Generator[Session]:
    """Dependency: provides a database session to route handlers.

    Yields a SQLAlchemy Session for each request, ensuring proper cleanup.

    Usage:
        def my_route(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
