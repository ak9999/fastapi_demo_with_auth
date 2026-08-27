from dataclasses import dataclass


@dataclass
class Person:
    """Domain entity representing a person."""

    first_name: str
    last_name: str
    age: int
    hometown: str
    id: int | None = None
