"""SQLAlchemy adapter for PersonRepository."""

from typing import cast

from sqlalchemy.orm import Session

from app.adapters.persistence.models import PersonModel
from app.domain.entities.person import Person


class SQLAlchemyPersonRepository:
    """Concrete implementation of PersonRepository using SQLAlchemy.

    Implements the PersonRepository protocol through structural typing.
    """

    def __init__(self, db: Session) -> None:
        """Initialize with a database session."""
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Person]:
        """Retrieve a page of persons from the database."""
        persons = self.db.query(PersonModel).offset(skip).limit(limit).all()
        return [self._model_to_entity(p) for p in persons]

    def get_by_id(self, person_id: int) -> Person | None:
        """Retrieve a person by ID."""
        person = self.db.query(PersonModel).filter(PersonModel.id == person_id).first()
        return self._model_to_entity(person) if person else None

    def create(self, person: Person) -> Person:
        """Create a new person in the database."""
        db_person = PersonModel(
            first_name=person.first_name,
            last_name=person.last_name,
            age=person.age,
            hometown=person.hometown,
        )
        self.db.add(db_person)
        self.db.commit()
        self.db.refresh(db_person)
        return self._model_to_entity(db_person)

    @staticmethod
    def _model_to_entity(model: PersonModel) -> Person:
        """Convert SQLAlchemy model to domain entity."""
        return Person(
            id=cast(int, model.id),
            first_name=cast(str, model.first_name),
            last_name=cast(str, model.last_name),
            age=cast(int, model.age),
            hometown=cast(str, model.hometown),
        )
