from typing import Protocol

from app.domain.entities.person import Person


class PersonRepository(Protocol):
    """Port: interface for person data access (structural typing)."""

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Person]:
        """Retrieve a page of persons."""
        ...

    def get_by_id(self, person_id: int) -> Person | None:
        """Retrieve a person by ID."""
        ...

    def create(self, person: Person) -> Person:
        """Create a new person."""
        ...
