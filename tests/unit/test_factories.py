"""Tests for Faker factories."""

from app.domain.entities.person import Person
from app.factories import person_factory


def test_person_factory_creates_valid_person() -> None:
    """Test that person_factory generates a valid Person with all required fields."""
    person = person_factory()

    assert isinstance(person, Person)
    assert isinstance(person.first_name, str)
    assert len(person.first_name) > 0
    assert isinstance(person.last_name, str)
    assert len(person.last_name) > 0
    assert isinstance(person.age, int)
    assert 18 <= person.age <= 100
    assert isinstance(person.hometown, str)
    assert len(person.hometown) > 0


def test_person_factory_generates_different_people() -> None:
    """Test that consecutive calls generate different people."""
    person1 = person_factory()
    person2 = person_factory()

    # At least one property should differ (statistically unlikely to be identical)
    properties_differ = (
        person1.first_name != person2.first_name
        or person1.last_name != person2.last_name
        or person1.age != person2.age
    )
    assert properties_differ


def test_person_factory_age_is_in_valid_range() -> None:
    """Test that generated ages are always within the expected range."""
    for _ in range(10):
        person = person_factory()
        assert 18 <= person.age <= 100


def test_person_factory_generates_non_empty_strings() -> None:
    """Test that all string fields are non-empty."""
    for _ in range(10):
        person = person_factory()
        assert person.first_name.strip()
        assert person.last_name.strip()
        assert person.hometown.strip()

