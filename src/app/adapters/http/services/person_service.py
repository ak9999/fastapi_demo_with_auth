"""Business logic for Person operations."""

from sqlalchemy.orm import Session

from app.adapters.persistence.person_repository import SQLAlchemyPersonRepository
from app.domain.entities.person import Person
from app.schemas.person import PersonRequest


class PersonService:
    """Service layer for Person operations."""

    def __init__(self, db: Session) -> None:
        """Initialize with database session and repository."""
        self.repository = SQLAlchemyPersonRepository(db)

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Person]:
        """Get a page of persons."""
        return self.repository.get_all(skip=skip, limit=limit)

    def get_by_id(self, person_id: int) -> Person | None:
        """Get a person by ID."""
        return self.repository.get_by_id(person_id)

    def create(self, person_request: PersonRequest) -> Person:
        """Create a new person."""
        person = Person(
            first_name=person_request.first_name,
            last_name=person_request.last_name,
            age=person_request.age,
            hometown=person_request.hometown,
        )
        return self.repository.create(person)
