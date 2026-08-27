# CLAUDE.md

Guidance for Claude Code (and any contributor, human or AI) working in this repository.

## Project Overview

A Python service built with **FastAPI**, using **Faker** for synthetic/test data generation. This document defines the conventions Claude should follow when writing, editing, or reviewing code in this repo.

## Tech Stack

- **Language:** Python 3.14
- **Web framework:** FastAPI
- **Test data:** Faker
- **Package/project management:** [uv](https://docs.astral.sh/uv/)
- **Linting/formatting:** ruff
- **Type checking:** mypy
- **Testing:** pytest, pytest-asyncio, pytest-cov

## Environment & Tooling

This project uses `uv` exclusively — do not use `pip`, `pip-tools`, `poetry`, or `venv` directly.

```bash
# Install/sync all dependencies (incl. dev group)
uv sync

# Add a runtime dependency
uv add <package>

# Add a dev dependency
uv add --dev <package>

# Run any command inside the project's environment
uv run <command>

# Run the app locally
uv run uvicorn src.app.main:app --reload

# Run linting
uv run ruff check .

# Auto-fix + format
uv run ruff check --fix .
uv run ruff format .

# Type check
uv run mypy .

# Run tests with coverage
uv run pytest --cov
```

Never edit `uv.lock` by hand. Never install packages outside of `uv add`/`uv sync`.

## Project Structure

Use a `src/app/` layout:

```
.
├── src/
│   └── app/
│       ├── __init__.py
│       ├── main.py            # FastAPI app instance, startup/shutdown
│       ├── domain/             # core business logic (entities, repository ports)
│       ├── adapters/           # implementations (HTTP routes, persistence)
│       │   ├── http/api/       # HTTP route handlers
│       │   └── persistence/    # database implementations
│       ├── schemas/            # Pydantic request/response schemas
│       ├── factories.py        # Faker-based factories for tests/seeding
│       └── deps.py             # (optional) shared FastAPI dependencies
├── tests/
│   ├── conftest.py
│   ├── unit/
│   └── integration/
├── pyproject.toml
├── uv.lock
└── CLAUDE.md
```

Architecture follows hexagonal (ports & adapters) pattern:
- **Domain** keeps business logic framework-agnostic (entities, abstract repository ports)
- **Adapters** implement concrete solutions (HTTP routes, database, Faker factories)
- **Schemas** define request/response boundaries

Keep routers thin: parse/validate input, delegate to domain/service logic, return response model.

## Code Style

No single external style guide is mandated — **ruff and mypy configuration in `pyproject.toml` are the source of truth**. In general, default to idiomatic, PEP 8–aligned Python and let tooling enforce it rather than debating style by hand. When in doubt, favor the same conventions Black/ruff-format already produce.

Key conventions Claude should follow:

- **Type hints are mandatory** on all function signatures (params + return type), including internal helpers. Run mypy in strict-ish mode; don't silence errors with unexplained `# type: ignore`.
- **Use modern typing syntax** available in 3.14: built-in generics (`list[int]`, `dict[str, Any]`), `X | None` instead of `Optional[X]`, `X | Y` instead of `Union[X, Y]`.
- **Docstrings**: use Google-style docstrings for any public function, class, or module that isn't self-evident from its name and type hints. Don't force docstrings onto trivial one-liners.
- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes and Pydantic models, `UPPER_SNAKE_CASE` for constants.
- **Imports**: absolute imports within the package; let `ruff` handle import sorting (isort rules) — don't hand-order imports.
- **Line length, quote style, formatting**: deferred entirely to `ruff format` — don't manually reformat against it.
- **Async by default** for I/O-bound FastAPI route handlers and service calls; don't mark something `async def` if it does no awaiting.
- **Avoid bare `except:`**; catch specific exceptions and raise `HTTPException` (or a custom exception + exception handler) at the API boundary, not deep in service code.
- **No mutable default arguments.**
- **Pydantic models** (v2 API) for all request/response schemas — don't pass raw dicts across layer boundaries.

## FastAPI Conventions

- One `APIRouter` per resource/domain, included in `main.py` via `app.include_router(...)`.
- Use FastAPI's dependency injection (`Depends`) for shared concerns: DB sessions, auth, settings, pagination — don't reach for globals.
- Response models declared explicitly via `response_model=` (or return-type annotation) so response shape is enforced and documented.
- Configuration via a Pydantic `BaseSettings` class in `core/config.py`, loaded from environment variables — no hardcoded config values in route/service code.
- Raise `fastapi.HTTPException` (or custom exceptions handled via `@app.exception_handler`) for error responses; don't return ad hoc error dicts with 200 status.

## Faker Conventions

- Centralize Faker-based test/seed data generation in `factories.py` modules (or `tests/factories.py`), not scattered `Faker()` calls inline in every test.
- Seed Faker (`Faker.seed(...)`) in test fixtures when a test asserts on specific generated values, to keep tests deterministic.
- Use a shared `Faker` instance/fixture (e.g. a pytest fixture in `conftest.py`) rather than instantiating `Faker()` repeatedly.
- Prefer Faker for realistic fixture data (names, emails, addresses, etc.) over hardcoded literal strings in tests, unless the specific value is the point of the test.

## Testing Conventions

- Test runner: `pytest`, configured in `pyproject.toml` (not a separate `pytest.ini`).
- Async tests use `pytest-asyncio`; prefer setting `asyncio_mode = "auto"` in config so `async def test_...` works without per-test markers — otherwise mark explicitly with `@pytest.mark.asyncio`.
- Use FastAPI's `TestClient` (sync) or an `httpx.AsyncClient` with `ASGITransport` (async) for endpoint tests — don't spin up a live server in tests.
- Split tests into `tests/unit/` (services, pure logic, no network/DB) and `tests/integration/` (API endpoints, DB-backed).
- Coverage via `pytest-cov`; run with `uv run pytest --cov=src --cov-report=term-missing`. Treat significant coverage drops as a signal to add tests, not just a number to chase.
- Test names describe behavior: `test_create_user_returns_409_when_email_exists`, not `test_create_user_2`.
- Use fixtures (`conftest.py`) for shared setup (test client, DB session, Faker instance) instead of duplicating setup per test.

## Commit / PR Hygiene

- Before considering a change done, run: `uv run ruff check .`, `uv run ruff format .`, `uv run mypy .`, `uv run pytest --cov`.
- Keep commits scoped to one logical change; don't mix formatting-only diffs with behavioral changes.

## What Claude Should Avoid

- Don't add new dependencies without adding them via `uv add`/`uv add --dev` (keep `pyproject.toml`/`uv.lock` in sync).
- Don't bypass type checking with broad `# type: ignore` or `Any` when a real type is available.
- Don't put business logic in route handlers or Pydantic model validators when it belongs in `services/`.
- Don't write non-deterministic tests (unseeded Faker output asserted directly, reliance on wall-clock time, etc.).
- Don't introduce a second HTTP client, test runner, or formatter/linter alongside the ones already chosen above.