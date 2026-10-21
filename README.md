# Secure Inventory Management API

A FastAPI REST API with MySQL, SQLAlchemy, Alembic, JWT authentication, Argon2 password hashing, refresh-token rotation, and role-based authorization.

## Features

- User registration and OAuth2 password login
- JWT access tokens and refresh tokens
- Refresh-token revocation and rotation
- Argon2 password hashing
- Admin, Manager, and Employee roles
- User activation and deactivation
- Layered repository and service architecture
- Alembic database migrations
- Protected inventory CRUD endpoints
- Swagger UI and automated tests

## Requirements

- Python 3.11 or later
- MySQL 8 or a compatible MySQL server
- Virtual environment
- Dependencies listed in `requirements.txt`

## Setup

1. Create and activate a virtual environment.
2. Install dependencies using `pip install -r requirements.txt`.
3. Create a MySQL database and configure `.env`.
4. Generate a strong JWT secret.
5. Review and apply Alembic migrations.
6. Start the API.

## Run the API

```cmd
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

## Authentication endpoints

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`

## User endpoints

- `GET /api/v1/users/me`
- `GET /api/v1/users`
- `PATCH /api/v1/users/{user_id}/role`
- `PATCH /api/v1/users/{user_id}/status`

## Database migrations

```cmd
alembic current
alembic revision --autogenerate -m "describe schema changes"
alembic upgrade head
```

Never modify an already-applied migration to introduce new schema changes. Create a new migration instead.

## Testing

```cmd
pytest -v
```

Use a dedicated test database for integration tests.

## Security

- Never commit `.env` or real credentials.
- Public registration assigns Employee by default.
- Admin-only operations require authorization.
- Store only refresh-token digests in the database.
- Use HTTPS in production.
- Keep dependencies updated and rotate compromised secrets.
- Configure backups and database permissions appropriately.

## Deployment

Use a production ASGI server configuration, HTTPS, secret management, monitoring, database backups, and a documented migration/rollback procedure. Do not use the development reload server in production.
