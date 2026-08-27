"""Integration tests for SQLAlchemyPersonRepository against a real database."""

from sqlalchemy.orm import Session

from app.adapters.persistence.person_repository import SQLAlchemyPersonRepository
from app.domain.entities.person import Person


def _make_person(n: int) -> Person:
    return Person(first_name=f"First{n}", last_name=f"Last{n}", age=20 + n, hometown="NYC")


def test_get_all_defaults_to_first_page(db_session: Session) -> None:
    """Test that get_all returns up to `limit` results starting from the beginning."""
    repository = SQLAlchemyPersonRepository(db_session)
    for n in range(5):
        repository.create(_make_person(n))

    page = repository.get_all()

    assert len(page) == 5


def test_get_all_respects_limit(db_session: Session) -> None:
    """Test that get_all returns no more than `limit` results."""
    repository = SQLAlchemyPersonRepository(db_session)
    for n in range(5):
        repository.create(_make_person(n))

    page = repository.get_all(limit=2)

    assert len(page) == 2


def test_get_all_respects_skip(db_session: Session) -> None:
    """Test that get_all skips the requested number of results."""
    repository = SQLAlchemyPersonRepository(db_session)
    for n in range(5):
        repository.create(_make_person(n))

    first_page = repository.get_all(skip=0, limit=2)
    second_page = repository.get_all(skip=2, limit=2)

    first_names_page_one = {p.first_name for p in first_page}
    first_names_page_two = {p.first_name for p in second_page}
    assert first_names_page_one.isdisjoint(first_names_page_two)


def test_get_all_returns_empty_list_when_skip_exceeds_count(db_session: Session) -> None:
    """Test that get_all returns an empty list when skip is beyond the available rows."""
    repository = SQLAlchemyPersonRepository(db_session)
    repository.create(_make_person(0))

    page = repository.get_all(skip=10, limit=10)

    assert page == []
