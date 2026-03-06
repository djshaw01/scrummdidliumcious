# scrummdidliumcious Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-03-05

## Active Technologies
- Python 3.11+ + Flask (routes and server-side rendering), SQLAlchemy (ORM), Alembic (schema migrations), Pydantic (boundary validation), psycopg (PostgreSQL driver), Jinja2 (templates), Flask-Sock (WebSocket transport for real-time events; chosen over polling to meet latency target with lower request overhead) (002-scrum-poker)
- PostgreSQL (preferred database flavor) (002-scrum-poker)

- Python 3.11+ + Flask (HTTP routing and template rendering), SQLAlchemy (required ORM baseline, no feature-specific models in this slice), Alembic (required migration workflow baseline), Pydantic (required boundary modeling baseline), psycopg (PostgreSQL driver), Jinja2 (HTML templating via Flask) (001-home-landing-page)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.11+: Follow standard conventions

## Recent Changes
- 002-scrum-poker: Added Python 3.11+ + Flask (routes and server-side rendering), SQLAlchemy (ORM), Alembic (schema migrations), Pydantic (boundary validation), psycopg (PostgreSQL driver), Jinja2 (templates), Flask-Sock (WebSocket transport for real-time events; chosen over polling to meet latency target with lower request overhead)

- 001-home-landing-page: Added Python 3.11+ + Flask (HTTP routing and template rendering), SQLAlchemy (required ORM baseline, no feature-specific models in this slice), Alembic (required migration workflow baseline), Pydantic (required boundary modeling baseline), psycopg (PostgreSQL driver), Jinja2 (HTML templating via Flask)

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
