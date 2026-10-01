# Portfolio Backend

FastAPI foundation for the portfolio application. Python `3.12.10` is the established runtime and the backend uses PostgreSQL through SQLAlchemy's async `asyncpg` driver.

## Setup

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
Copy-Item .env.example .env
```

Set a real `DATABASE_URL` and `JWT_SECRET_KEY` in `.env`. Production rejects the development JWT secret and requires at least 32 characters. Apply schema changes with `alembic upgrade head`; application startup never creates tables.

Run the API with `uvicorn app.main:app --reload`. Create the first administrator after migrating with `.\\.venv\\Scripts\\python.exe scripts\\create_admin.py` from `backend`; credentials may be supplied through `BOOTSTRAP_ADMIN_EMAIL` and `BOOTSTRAP_ADMIN_PASSWORD`, or entered interactively without printing the password.

Run tests with `pytest`.

## Dependency purposes

- FastAPI/Uvicorn: HTTP API and ASGI serving.
- SQLAlchemy/asyncpg/Alembic: async PostgreSQL persistence and migrations.
- Pydantic Settings: typed environment configuration.
- PyJWT: signed short-lived access tokens.
- argon2-cffi: Argon2id password hashing.
- structlog: structured request/application logs.
- pytest/pytest-asyncio/HTTPX/aiosqlite: async API and database tests.
