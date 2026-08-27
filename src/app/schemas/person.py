from pydantic import BaseModel


class PersonRequest(BaseModel):
    """Request schema for creating a person."""

    first_name: str
    last_name: str
    age: int
    hometown: str


class PersonResponse(BaseModel):
    """Response schema for a person."""

    id: int
    first_name: str
    last_name: str
    age: int
    hometown: str
