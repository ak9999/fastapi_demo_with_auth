"""Tests for domain entities."""

from app.domain.entities.person import Person


def test_person_can_be_instantiated() -> None:
    """Test that Person entity can be created with required fields."""
    person = Person(first_name="John", last_name="Doe", age=30, hometown="NYC")

    assert person.first_name == "John"
    assert person.last_name == "Doe"
    assert person.age == 30
    assert person.hometown == "NYC"


def test_person_is_dataclass() -> None:
    """Test that Person behaves as a dataclass."""
    person1 = Person(first_name="Alice", last_name="Smith", age=25, hometown="LA")
    person2 = Person(first_name="Alice", last_name="Smith", age=25, hometown="LA")

    assert person1 == person2


def test_person_with_different_values_are_not_equal() -> None:
    """Test that Person instances with different values are not equal."""
    person1 = Person(first_name="Alice", last_name="Smith", age=25, hometown="LA")
    person2 = Person(first_name="Bob", last_name="Smith", age=25, hometown="LA")

    assert person1 != person2
