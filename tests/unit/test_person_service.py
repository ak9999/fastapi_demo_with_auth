"""Unit tests for PersonService."""

from sqlalchemy.orm import Session

from app.adapters.http.services.person_service import PersonService
from app.schemas.person import PersonRequest


def test_create_persists_and_returns_person(db_session: Session) -> None:
    service = PersonService(db_session)
    request = PersonRequest(
        first_name="Grace", last_name="Hopper", age=85, hometown="NYC"
    )

    person = service.create(request)

    assert person.id is not None
    assert person.first_name == "Grace"


def test_get_by_id_returns_none_when_missing(db_session: Session) -> None:
    service = PersonService(db_session)

    assert service.get_by_id(999) is None


def test_get_by_id_returns_person_when_present(db_session: Session) -> None:
    service = PersonService(db_session)
    created = service.create(
        PersonRequest(first_name="Alan", last_name="Turing", age=41, hometown="London")
    )

    found = service.get_by_id(created.id)  # type: ignore[arg-type]

    assert found == created


def test_get_all_returns_created_persons(db_session: Session) -> None:
    service = PersonService(db_session)
    service.create(PersonRequest(first_name="A", last_name="B", age=1, hometown="C"))

    persons = service.get_all()

    assert len(persons) == 1
