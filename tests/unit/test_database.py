"""Unit tests for the get_db session dependency."""

from sqlalchemy.orm import Session

from app.core.database import get_db


def test_get_db_yields_session_and_closes_it() -> None:
    generator = get_db()

    db = next(generator)

    assert isinstance(db, Session)

    generator.close()
