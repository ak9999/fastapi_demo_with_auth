"""Tests for Pydantic schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.person import PersonRequest, PersonResponse


def test_person_request_can_be_created() -> None:
    """Test that PersonRequest schema can be instantiated."""
    request = PersonRequest(
        first_name="John", last_name="Doe", age=30, hometown="NYC"
    )

    assert request.first_name == "John"
    assert request.last_name == "Doe"
    assert request.age == 30
    assert request.hometown == "NYC"


def test_person_request_validates_required_fields() -> None:
    """Test that PersonRequest requires all fields."""
    with pytest.raises(ValidationError):
        PersonRequest(first_name="John", last_name="Doe", age=30)  # type: ignore


def test_person_response_can_be_created() -> None:
    """Test that PersonResponse schema can be instantiated."""
    response = PersonResponse(
        id=1, first_name="John", last_name="Doe", age=30, hometown="NYC"
    )

    assert response.id == 1
    assert response.first_name == "John"
    assert response.last_name == "Doe"
    assert response.age == 30
    assert response.hometown == "NYC"


def test_person_request_serializes_to_dict() -> None:
    """Test that PersonRequest can be converted to dict."""
    request = PersonRequest(
        first_name="John", last_name="Doe", age=30, hometown="NYC"
    )
    data = request.model_dump()

    assert data == {
        "first_name": "John",
        "last_name": "Doe",
        "age": 30,
        "hometown": "NYC",
    }
