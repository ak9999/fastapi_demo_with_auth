"""Faker-based factories for generating test data."""

from faker import Faker

from .domain.entities.person import Person

faker = Faker()


def person_factory() -> Person:
    """Generate a fake person with realistic data."""
    return Person(
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        age=faker.random_int(min=18, max=100),
        hometown=faker.city(),
    )
