"""Tests for repository protocol structure."""

from typing import get_type_hints

from app.domain.repositories.person_repository import PersonRepository


def test_person_repository_protocol_has_required_methods() -> None:
    """Test that PersonRepository protocol defines the expected methods."""
    methods = [method for method in dir(PersonRepository) if not method.startswith("_")]

    assert "get_all" in methods
    assert "get_by_id" in methods
    assert "create" in methods


def test_person_repository_protocol_method_signatures() -> None:
    """Test that PersonRepository methods have correct type hints."""
    hints = get_type_hints(PersonRepository.get_all)
    assert "return" in hints

    hints = get_type_hints(PersonRepository.get_by_id)
    assert "person_id" in hints
    assert "return" in hints

    hints = get_type_hints(PersonRepository.create)
    assert "person" in hints
    assert "return" in hints
