"""Integration tests for the persons HTTP API."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.adapters.http.api.person import _to_response
from app.core.database import get_db
from app.domain.entities.person import Person
from app.main import app


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient]:
    app.dependency_overrides[get_db] = lambda: db_session
    try:
        yield TestClient(app)
    finally:
        del app.dependency_overrides[get_db]


def _person_payload() -> dict[str, object]:
    return {
        "first_name": "Ada",
        "last_name": "Lovelace",
        "age": 30,
        "hometown": "London",
    }


def test_create_person_returns_201_with_created_person(client: TestClient) -> None:
    response = client.post("/persons", json=_person_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["first_name"] == "Ada"
    assert body["id"] is not None


def test_list_persons_returns_created_persons(client: TestClient) -> None:
    client.post("/persons", json=_person_payload())

    response = client.get("/persons")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_list_persons_respects_pagination_params(client: TestClient) -> None:
    for n in range(3):
        payload = _person_payload()
        payload["first_name"] = f"Person{n}"
        client.post("/persons", json=payload)

    response = client.get("/persons", params={"skip": 1, "limit": 1})

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_person_returns_200_when_found(client: TestClient) -> None:
    created = client.post("/persons", json=_person_payload()).json()

    response = client.get(f"/persons/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


def test_get_person_returns_404_when_not_found(client: TestClient) -> None:
    response = client.get("/persons/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Person not found"}


def test_to_response_raises_for_unpersisted_person() -> None:
    person = Person(first_name="Ada", last_name="Lovelace", age=30, hometown="London")

    with pytest.raises(ValueError, match="unpersisted Person"):
        _to_response(person)
