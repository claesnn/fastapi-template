# Repository Guidelines

## Project Structure & Module Organization
Source code lives in `src/`, with the FastAPI entry point at `src/main.py` and shared infrastructure (settings, database, logger, middleware) at the top level. Domain logic is grouped under `src/features/<domain>` with parallel `models.py`, `schemas.py`, `services.py`, and `routes.py` modules that keep APIs, persistence, and DTOs aligned. Database migrations are tracked in `src/alembic/` and pick up metadata from `settings.py`. Tests mirror the feature layout in `tests/` and rely on fixtures from `tests/conftest.py` to boot the app and provide an async SQLite database.

## Build, Test, and Development Commands
- `python -m venv .venv && source .venv/bin/activate` sets up the recommended virtual environment.
- `pip install -r requirements.txt` installs FastAPI, SQLAlchemy, Alembic, and the test stack.
- `fastapi dev` runs the app with auto-reload using configuration from `.env`.
- `alembic upgrade head` applies the latest migrations (run from `src/` so the env module resolves correctly).
- `pytest -v` executes the async API tests; add `-k users` or `tests/test_todos.py` to focus on a feature.
- Every request (including tests and docs) must include `Authorization: Bearer Nina`, otherwise the auth middleware returns `403`.

## Coding Style & Naming Conventions
Follow PEP 8 with 4-space indentation, type hints on public functions, and `snake_case` for module, function, and variable names. Classes (including Pydantic models) use `PascalCase`, while routers and services stay `snake_case`. Keep async service calls awaited at the route layer and log structured messages through the shared `logger`. New feature folders should replicate the existing file layout and register routers in `main.py`.

## Transaction Handling
Mutating endpoints open their own `async with db.begin()` blocks so each request wraps its changes in an explicit transaction. Service methods that modify state expose a `flush` keyword (default `True`) so they can opt out of flushing when participating in a broader transaction boundary—override it with `flush=False` when composing multiple writes inside the same session.

## Testing Guidelines
Write `pytest`-style tests under `tests/` using `async def` when exercising endpoints or services. Name files `test_<feature>.py` and functions `test_<behavior>` to match the current suite. Use the provided fixtures to get an `AsyncClient` and session rather than opening real connections. Ensure new endpoints or data access paths have coverage, and run `pytest -v --maxfail=1` before submitting to catch regressions early.

## Commit & Pull Request Guidelines
Compose commit messages in the imperative mood (`Add todo filtering`, `Fix user schema validation`) and keep related changes together. Pull requests should explain the user-facing impact, reference any issue IDs, and list relevant follow-up tasks. Include reproduction steps or screenshots for API or schema changes, note any migration commands that must be run, and paste the `pytest` output when practical.

## Environment & Configuration Notes
Create `.env` from `.env.example` and set `DB_URL` before running the app locally. Alembic derives settings from `settings.Settings`, so keep schema changes aligned with the ORM models. Structured JSON logs are emitted by default; adjust collector settings in `logger.py` if your deployment target requires different formatting.
