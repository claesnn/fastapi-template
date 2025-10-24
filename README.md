# FastAPI Template

Asynchronous FastAPI starter that uses SQLAlchemy 2.0, Alembic migrations, and Pydantic v2 schemas to deliver CRUD APIs for users and todos. The project is structured for easy feature expansion, observability with JSON logging, and automated testing.

## Features

- Async FastAPI application with modular `features/*` packages for domain isolation
- SQLAlchemy 2.0 ORM models with async sessions and relationship loading helpers
- Alembic migrations wired to the shared settings module for database upgrades
- Pydantic v2 schemas (including relational projections) to drive request/response validation
- Structlog JSON logging ready for production aggregators
- Pytest + httpx test suite with an in-memory async SQLite database fixture

## Requirements

- Python 3.11+
- `pip` for installing dependencies
- A database supported by SQLAlchemy (default examples use SQLite/PostgreSQL)

## Getting Started

1. **Clone and enter the project**
   ```pwsh
   git clone <your-fork-url> fastapi-template
   cd fastapi-template
   ```
2. **Install dependencies with UV**
   ```pwsh
   uv sync
   ```
3. **Configure environment variables**
   Copy `.env.example` to `.env` (or create `.env`) and set at least `DB_URL`.

   ```env
   DB_URL=sqlite+aiosqlite:///./data.db
   ```

   The `settings.Settings` class reads from `.env` via `pydantic-settings`.

## Running the Application

1. Apply migrations (optional for SQLite, required for persisted databases):
   ```pwsh
   cd src
   alembic upgrade head
   ```
2. Start the FastAPI app:
   ```pwsh
   fastapi dev
   ```
3. The API enforces a simple bearer token check. Supply `Authorization: Bearer Nina` on every request (including Swagger “Authorize”) to avoid `403` responses.
4. Visit the interactive docs at `http://localhost:8000/docs` or the alternative schema at `http://localhost:8000/redoc`.

> **Note:** The included logging configuration emits ISO-timestamped JSON to stdout via Structlog.

## Running Tests

Execute the asynchronous API tests (uses an in-memory database):
```pwsh
pytest -v
```

## Transaction Handling

Mutating route handlers own the transaction boundary by opening `async with db.begin()` blocks before invoking their services. This keeps commits scoped to a single HTTP lifecycle and makes rollbacks predictable. The corresponding service methods expose an optional `flush` flag (defaulting to `True` for most creates and updates) so they can be reused inside larger workflows without forcing an early flush—pass `flush=False` when composing multiple operations inside an existing transaction.

## Database Migrations

- Create a new revision:
  ```pwsh
  cd src
  alembic revision -m "add new table"
  ```
- Apply the latest migrations:
  ```pwsh
  alembic upgrade head
  ```

Alembic loads the SQLAlchemy URL from `settings.db_url`, so keep `.env` in sync.

## Project Layout

```
.
├── requirements.txt
├── src
│   ├── main.py              # FastAPI app & router wiring
│   ├── settings.py          # Pydantic settings (reads DB_URL)
│   ├── database.py          # Async engine, session factory, Base
│   ├── logger.py            # Structlog JSON logger
│   ├── features
│   │   ├── users            # User domain: models, routes, services, schemas
│   │   └── todos            # Todo domain: models, routes, services, schemas
│   └── alembic              # Migration environment & versions
└── tests
    ├── test_users.py        # Async API tests for user endpoints
    └── test_todos.py        # Async API tests for todo endpoints
```

## API Overview

### Users
- `POST /users/` – Create a user
- `GET /users/{user_id}` – Retrieve a user
- `GET /users/` – List users
- `PATCH /users/{user_id}` – Update partial fields
- `DELETE /users/{user_id}` – Remove a user

### Todos
- `POST /todos/` – Create a todo
- `GET /todos/{todo_id}` – Retrieve a todo
- `GET /todos/` – List todos
- `GET /todos/with-users` – List todos with optional user details
- `PATCH /todos/{todo_id}` – Update a todo
- `DELETE /todos/{todo_id}` – Remove a todo

Todos can optionally be linked to users via `user_id`, and the `TodoService` verifies the referenced user exists before insertion.

### Pagination
Collection endpoints accept `page` (default `1`) and `page_size` (default `20`, max `100`). Responses return a consistent envelope:

```json
{
  "items": [...],
  "total": 42,
  "page": 1,
  "page_size": 20
}
```

Use `/todos/with-users` when you need eager-loaded user data alongside todos.

## Extending the Template

- Add new feature folders under `src/features/<domain>` following the patterns for models, schemas, services, and routes.
- Register new routers in `src/main.py`.
- Use the existing dependency injection helpers to access the async session or cross-feature services.
- Update tests to cover new endpoints using the fixtures in `tests/conftest.py`.
- Add models import to `src/alembic/env.py`
- To migrate new models: Make revisions and upgrade database

## Tooling Tips

- Use `fastapi dev` for auto-reload with rapid prototyping.
- Override dependencies in tests via `app.dependency_overrides` as demonstrated in `tests/conftest.py`.
- Enable structured logging aggregation by shipping stdout to your log collector of choice.
