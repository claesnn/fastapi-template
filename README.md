# FastAPI Template

Asynchronous FastAPI starter that combines SQLAlchemy 2.0, Alembic migrations, and Pydantic v2 schemas to deliver modular CRUD APIs for users and todos while enforcing bearer authentication and emitting structured JSON logs.

## Highlights
- Global HTTP bearer guard (`Authorization: Bearer Nina`) backed by `HTTPBearer` and reusable auth helpers.
- Modular domain packages in `src/features/<domain>` with aligned `models`, `schemas`, `services`, and `routes` modules.
- SQLAlchemy 2.0 async stack with explicit `async with db.begin()` transaction boundaries.
- Structlog-powered request middleware that stamps each response with an `X-Request-ID` and logs duration, status, and endpoint.
- Shared pagination helpers that return a consistent `{items,total,page,page_size}` payload.
- Health and status probes (`GET /` and `GET /health`) for readiness checks.

## Prerequisites
- Python 3.11+
- SQLite (default), or any SQLAlchemy-supported database URL for `settings.db_url`
- Optional: [uv](https://github.com/astral-sh/uv) for fast dependency management

## Quickstart
1. **Clone the repository**
   ```bash
   git clone <your-fork-url> fastapi-template
   cd fastapi-template
   ```
2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. **Install dependencies**
   ```bash
   pip install -e .
   # Install test tooling if you plan to run the suite
   pip install pytest pytest-asyncio
   ```
   Or, if you use `uv`:
   ```bash
   uv sync
   ```

## Environment Configuration
Create `.env` in the project root (the `Settings` object in `src/settings.py` loads it automatically). At minimum set a database URL; SQLite is convenient for local work:
```env
db_url=sqlite+aiosqlite:///./data.db
log_level=DEBUG
cors_allow_origins=http://localhost:3000,http://localhost:5173
```
Comma-separated values are expanded into lists for the CORS settings.

## Running the Application
1. **Apply migrations** (run from `src/` so Alembic can locate `env.py`):
   ```bash
   cd src
   alembic upgrade head
   ```
2. **Start the API with auto-reload**:
   ```bash
   fastapi dev
   ```
3. **Authenticate every request** with `Authorization: Bearer Nina` (including the Swagger “Authorize” dialog) to avoid `401` responses.
4. Visit `http://localhost:8000/docs` for the interactive schema or `http://localhost:8000/redoc` for an alternative view.

Logs are JSON-formatted and include request metadata emitted by `StructlogRequestMiddleware`.

## Database Migrations
- Create a revision:
  ```bash
  cd src
  alembic revision -m "add new table"
  ```
- Apply the latest migration:
  ```bash
  alembic upgrade head
  ```

Alembic reads the SQLAlchemy URL from `settings.db_url`, so keep `.env` in sync with your target database.

## API Surface
- `GET /` – Lightweight status check that logs a debug entry.
- `GET /health` – Pings the database; returns `500` if the connection fails.

### Users
- `POST /users/` – Create a user (transactional)
- `GET /users/{user_id}` – Retrieve a single user
- `GET /users/` – List users with pagination
- `PATCH /users/{user_id}` – Partially update a user (transactional)
- `DELETE /users/{user_id}` – Remove a user (transactional)

### Todos
- `POST /todos/` – Create a todo, verifying referenced users exist (transactional)
- `GET /todos/{todo_id}` – Retrieve a todo
- `GET /todos/` – List todos with pagination
- `GET /todos/with-users` – List todos and optionally eager-load related users
- `PATCH /todos/{todo_id}` – Update a todo (transactional)
- `DELETE /todos/{todo_id}` – Remove a todo (transactional)

Paginated responses return:
```json
{
  "items": [...],
  "total": 42,
  "page": 1,
  "page_size": 20
}
```
Use the `page` and `page_size` query parameters (max `100`) to control pagination.

## Testing
Run the async API suite (uses an in-memory SQLite database) after activating your virtual environment:
```bash
pytest -v --maxfail=1
```
Fixtures in `tests/conftest.py` handle app bootstrapping, dependency overrides, and injecting the required bearer token so integration tests mirror real requests.

## Project Layout
```
.
├── AGENTS.md
├── pyproject.toml
├── uv.lock
├── src
│   ├── main.py            # FastAPI app & router wiring
│   ├── middleware.py      # Structlog request middleware
│   ├── settings.py        # Pydantic settings (loads .env)
│   ├── database.py        # Async engine, session factory, DeclarativeBase
│   ├── logger.py          # Structlog configuration
│   ├── alembic            # Migration environment & versions
│   └── features
│       ├── auth           # HTTP bearer dependency
│       ├── common         # Pagination and shared utilities
│       ├── todos          # Todo domain models/routes/services/schemas
│       └── users          # User domain models/routes/services/schemas
└── tests
    ├── conftest.py        # Async test fixtures & client factory
    ├── test_todos.py
    └── test_users.py
```

## Extending the Template
- Add a new folder under `src/features/<domain>` and mirror the existing `models`, `schemas`, `services`, and `routes` structure.
- Import new models in `src/alembic/env.py` so Alembic picks them up, then generate migrations.
- Register the router in `src/main.py` to expose endpoints.
- Cover new behaviors with tests in `tests/` using the provided fixtures.
- Wrap multi-operation writes in a shared `async with db.begin()` block and pass `flush=False` into services that participate in wider transactions.

## Tooling Notes
- `fastapi dev` watches the project for code changes and reloads automatically.
- Structured logs bind request metadata (method, path, status, duration, request id) so collectors can index and search easily.
- Global CORS settings are read from `.env`; provide comma-separated lists for origins, headers, or methods when tightening access for different environments.
