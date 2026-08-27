"""One-off script to pre-populate app.db with fake Person records.

Usage:
    uv run python scripts/fill_db.py [--count COUNT]
"""

import argparse

from app.adapters.persistence.person_repository import SQLAlchemyPersonRepository
from app.core.database import SessionLocal
from app.factories import person_factory


def fill_db(count: int) -> None:
    """Insert `count` fake persons into the existing database."""
    db = SessionLocal()
    try:
        repository = SQLAlchemyPersonRepository(db)
        for _ in range(count):
            repository.create(person_factory())
    finally:
        db.close()


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for this script."""
    parser = argparse.ArgumentParser(description="Pre-populate app.db with fake Person records.")
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of fake persons to insert (default: 10)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    fill_db(args.count)
    print(f"Inserted {args.count} fake persons into app.db")
