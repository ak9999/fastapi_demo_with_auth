"""HTTP adapter for person endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.adapters.http.services.person_service import PersonService
from app.core.database import get_db
from app.domain.entities.person import Person
from app.schemas.person import PersonRequest, PersonResponse

router = APIRouter(prefix="/persons", tags=["persons"])


def _to_response(person: Person) -> PersonResponse:
    """Convert a persisted Person entity to its API response schema.

    Only ever called with persons that have been loaded from or written to the
    database, so `person.id` is expected to be set.
    """
    if person.id is None:
        raise ValueError("Cannot build a PersonResponse for an unpersisted Person")
    return PersonResponse(
        id=person.id,
        first_name=person.first_name,
        last_name=person.last_name,
        age=person.age,
        hometown=person.hometown,
    )


@router.get("", response_model=list[PersonResponse])
def list_persons(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),  # noqa: B008
) -> list[PersonResponse]:
    """List persons, paginated via skip/limit query params."""
    service = PersonService(db)
    persons = service.get_all(skip=skip, limit=limit)
    return [_to_response(p) for p in persons]


@router.post("", response_model=PersonResponse, status_code=201)
def create_person(
    person_request: PersonRequest, db: Session = Depends(get_db)  # noqa: B008
) -> PersonResponse:
    """Create a new person."""
    service = PersonService(db)
    person = service.create(person_request)
    return _to_response(person)


@router.get("/{person_id}", response_model=PersonResponse)
def get_person(person_id: int, db: Session = Depends(get_db)) -> PersonResponse:  # noqa: B008
    """Get a person by ID."""
    service = PersonService(db)
    person = service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return _to_response(person)
