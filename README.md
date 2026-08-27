# FastAPI + Auth

A FastAPI application demonstrating hexagonal architecture patterns, built with Python 3.14 and modern web development practices.

## Tech Stack

- **Framework:** FastAPI
- **Language:** Python 3.14
- **Package Manager:** [uv](https://docs.astral.sh/uv/)
- **Testing:** pytest, pytest-asyncio, pytest-cov
- **Type Checking:** mypy
- **Linting/Formatting:** ruff
- **Test Data:** Faker

## Architecture

This project follows **hexagonal (ports & adapters) architecture**:

- **Domain** (`src/app/domain/`) — Core business logic, framework-agnostic entities and port interfaces
- **Adapters** (`src/app/adapters/`) — Concrete implementations for HTTP routes, database persistence, etc.
- **Schemas** (`src/app/schemas/`) — Pydantic request/response models at API boundaries
- **Factories** (`src/app/factories.py`) — Faker-based test data generation

This separation ensures business logic is decoupled from framework specifics, making the code testable and maintainable.

## Getting Started

### Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

```bash
# Clone/enter the project directory
cd fastapi-pingfed-demo

# Sync dependencies (including dev)
uv sync
```

### Running the App

```bash
# Development (with auto-reload)
uv run uvicorn src.app.main:app --reload

# Production
uv run uvicorn src.app.main:app --workers 4
```

The API will be available at `http://localhost:8000`

- Interactive docs: `http://localhost:8000/docs` (Swagger UI)
- Alternative docs: `http://localhost:8000/redoc` (ReDoc)
- Health check (liveness): `http://localhost:8000/health/live`
- Health check (readiness): `http://localhost:8000/health/ready`

## Configuration

Application settings live in [`src/app/core/config.py`](src/app/core/config.py) as a Pydantic `Settings` class, sourced from environment variables (or a local `.env` file). Every variable is prefixed with `APP_`.

| Variable                    | Default                              | Description                                             |
| --------------------------- | ------------------------------------- | -------------------------------------------------------- |
| `APP_DATABASE_URL`          | `sqlite:///./app.db`                  | SQLAlchemy database connection URL                        |
| `APP_SESSION_SECRET_KEY`    | `insecure-dev-secret-change-me`       | Key used to sign the session cookie — set a real secret in production |
| `APP_OAUTH_ISSUER`          | `""`                                   | OIDC issuer URL (e.g. Keycloak's realm URL) — its `.well-known/openid-configuration` is derived from this |
| `APP_OAUTH_CLIENT_ID`       | `""`                                   | OAuth client ID registered with the identity provider     |
| `APP_OAUTH_CLIENT_SECRET`   | `""`                                   | OAuth client secret registered with the identity provider |
| `APP_OAUTH_REDIRECT_URI`    | `http://localhost:8000/auth/callback` | Callback URL registered with the OAuth client              |
| `APP_OAUTH_SCOPES`          | `openid profile email`                | Space-separated OIDC scopes requested at login             |

The provider is configured entirely through these `APP_OAUTH_*` variables, so swapping Keycloak for another OIDC provider (Okta, Auth0, PingFederate, ...) is just a config change, provided it exposes an OIDC discovery document.

To override a setting, either export it in your shell:

```bash
APP_DATABASE_URL="postgresql://user:pass@localhost/db" uv run app-dev
```

or create a `.env` file in the project root (this file is gitignored and should never be committed):

```bash
# .env
APP_DATABASE_URL=sqlite:///./app.db
```

To add a new setting, add a field to the `Settings` class in `core/config.py` — it's picked up automatically from the environment using the `APP_` prefix.

## Authentication

`/` is guarded by an OIDC authorization code flow (see [`src/app/core/security.py`](src/app/core/security.py) and [`src/app/adapters/http/api/auth.py`](src/app/adapters/http/api/auth.py)). This project uses [Keycloak](https://www.keycloak.org/) as its identity provider, though any OIDC-compliant provider works (Okta, Auth0, PingFederate, etc.) — configured entirely through the `APP_OAUTH_*` environment variables above.

### Setup

1. Register a client application with your identity provider and note its client ID/secret.
2. Register `APP_OAUTH_REDIRECT_URI` (default `http://localhost:8000/auth/callback`) as an allowed redirect URI on that client.
3. Set the environment variables, e.g. in a `.env` file:

   ```bash
   # .env
   APP_OAUTH_ISSUER=https://your-issuer-host
   APP_OAUTH_CLIENT_ID=your-client-id
   APP_OAUTH_CLIENT_SECRET=your-client-secret
   APP_OAUTH_REDIRECT_URI=http://localhost:8000/auth/callback
   APP_OAUTH_SCOPES=openid profile email
   APP_SESSION_SECRET_KEY=a-long-random-secret
   ```

   `APP_OAUTH_ISSUER` must serve a standard `{issuer}/.well-known/openid-configuration` discovery document — that's how the app locates the provider's authorization, token, and userinfo endpoints.

### Usage

- **`GET /`** — renders an HTML page: a "Log in" link when there's no session, or a greeting + "Log out" link when there is.
- **`GET /auth/login`** — starts the authorization code flow, redirecting to the provider's login page.
- **`GET /auth/callback`** — the registered redirect URI; exchanges the authorization code for tokens, fetches the user's claims, and stores them in a signed session cookie.
- **`GET /auth/logout`** — clears the local session (does not perform provider-side single logout).

To guard a route so it rejects instead of rendering a logged-out state, use `user: dict[str, Any] = Depends(get_current_user)`; to render conditionally like `/` does, use `get_optional_user` instead (see [`src/app/api/root.py`](src/app/api/root.py) and [`src/app/core/security.py`](src/app/core/security.py)). No per-provider code is needed either way.

### Running Keycloak locally

[`podman-compose.yml`](podman-compose.yml) brings up a local [Keycloak](https://www.keycloak.org/) instance (Docker Hub's official `keycloak/keycloak` image, run in dev mode with an in-memory store) so you have a real OIDC provider to wire the app up to. No license or account is needed.

1. Copy [`.env.keycloak.example`](.env.keycloak.example) to `.env.keycloak` — the defaults (`admin`/`admin`) are fine for local dev.
2. Start the container:

   ```bash
   podman-compose --env-file .env.keycloak -f podman-compose.yml up -d
   ```

3. Open the admin console at `http://localhost:8080` and log in with the admin credentials from `.env.keycloak`.
4. Create a realm (e.g. `demo`) — top-left realm dropdown → **Create realm**.
5. Create a client in that realm — **Clients** → **Create client**:
   - Client ID: anything, e.g. `fastapi-demo`
   - Client authentication: **On** (confidential client, so it gets a secret)
   - Valid redirect URIs: `http://localhost:8000/auth/callback`
6. On the client's **Credentials** tab, copy the client secret.
7. Create at least one user under **Users** (with a password, under the **Credentials** tab) so you have something to log in as.
8. Fill in `.env`:

   ```bash
   APP_OAUTH_ISSUER=http://localhost:8080/realms/demo
   APP_OAUTH_CLIENT_ID=fastapi-demo
   APP_OAUTH_CLIENT_SECRET=<the secret from step 6>
   ```

Keycloak's dev-mode container serves plain HTTP, so there's no self-signed cert to work around locally.

To stop everything: `podman-compose --env-file .env.keycloak -f podman-compose.yml down`. Data persists in a named volume between restarts; add `-v` to `down` to wipe it.

### Custom login theme

[`keycloak-theme/demo/`](keycloak-theme/demo/) is a CSS-only Keycloak theme that restyles the default login page to match this app's `/` page (same font, centered layout, blue button) instead of writing Keycloak's `login.ftl` from scratch — Keycloak's own form logic (CSRF, MFA, social login, error states) stays intact, only its `login.css` gets overridden. `podman-compose.yml` already mounts it into the container at `/opt/keycloak/themes/demo`.

To enable it: in the Keycloak admin console, go to your realm → **Realm settings** → **Themes** tab → set **Login theme** to `demo` → **Save**. Reload `/auth/login` to see it applied.

Keycloak's markup/class names can shift between versions — if a style doesn't take, open devtools on the login page, find the element, and adjust the matching selector in [`login.css`](keycloak-theme/demo/login/resources/css/login.css).

## Development

### Running Tests

```bash
# Run all tests with coverage
uv run pytest

# Run specific test file
uv run pytest tests/unit/test_factories.py -v

# Run with specific verbosity
uv run pytest -vv
```

### Code Quality

```bash
# Type checking
uv run mypy .

# Linting
uv run ruff check .

# Auto-fix + format
uv run ruff check --fix .
uv run ruff format .
```

**Before committing, run all checks:**
```bash
uv run ruff check . && uv run ruff format . && uv run mypy . && uv run pytest --cov
```

### Project Structure

```
src/app/
├── domain/              # Business logic (entities, repository ports)
│   ├── entities/        # Domain models (e.g., Person)
│   └── repositories/    # Abstract port interfaces (Protocols)
├── adapters/            # Framework implementations
│   ├── http/
│   │   ├── api/         # FastAPI route handlers (incl. auth.py — OIDC login/callback/logout)
│   │   └── services/    # Business logic between routes and repositories
│   └── persistence/     # SQLAlchemy models + repository implementations
├── api/                 # Legacy routers (health checks, root)
├── core/
│   ├── config.py        # Pydantic Settings, loaded from environment variables
│   ├── database.py      # SQLAlchemy engine/session setup
│   └── security.py      # OIDC client + get_current_user auth dependency
├── schemas/              # Pydantic request/response models
├── factories.py          # Faker test data factories
├── cli.py                # `app-dev` / `app-prod` entry points
└── main.py               # FastAPI app setup

tests/
├── conftest.py          # Shared pytest fixtures (Faker, in-memory DB session)
├── unit/                # Unit tests (pure logic, no I/O)
└── integration/         # Integration tests (repository against real DB)
```

## Key Concepts

### Hexagonal Architecture

- **Ports** (interfaces): Abstract definitions of external service contracts (`domain/repositories/`)
- **Adapters** (implementations): Concrete implementations for specific technologies (`adapters/`)
- **Domain**: Core business logic independent of frameworks

Benefits:
- Testability — swap implementations easily
- Maintainability — clear separation of concerns
- Flexibility — technology choices isolated to adapters

### Protocol-Based Interfaces

This project uses Python's `typing.Protocol` for port definitions instead of ABC (Abstract Base Classes). Protocols provide structural typing — implementations don't need to explicitly inherit, just implement the required methods.

### Faker Factories

Test data is generated using Faker through centralized factories (`factories.py`). This ensures consistent, realistic test data without hardcoded values.

## Development Conventions

See [CLAUDE.md](CLAUDE.md) for detailed coding conventions including:

- Type hints (mandatory on all functions)
- Modern Python 3.14 syntax
- Pydantic v2 for schemas
- Async-first for I/O operations
- FastAPI dependency injection patterns

## Health Checks

The application exposes two health check endpoints for container orchestration:

- **`GET /health/live`** — Liveness probe (is the process running?)
- **`GET /health/ready`** — Readiness probe (is the app ready to serve requests?)

Both return `200` when healthy. Implement dependency checks in the readiness endpoint when adding database connections or external service integrations.

## Next Steps

- [x] Implement SQLAlchemy models and database integration
- [x] Add Person CRUD endpoints (list, create, get by id — paginated)
- [x] Implement PersonRepository with SQLAlchemy adapter
- [x] Add integration tests for the repository against a real database
- [ ] Add integration tests for the HTTP endpoints
- [ ] Add update/delete Person endpoints
- [ ] Add database migrations (Alembic)
- [x] Add authentication/authorization with Keycloak (guards `/`; more routes to follow)
- [ ] Add request logging and observability

---

**Built with:** FastAPI | Python 3.14 | Hexagonal Architecture
