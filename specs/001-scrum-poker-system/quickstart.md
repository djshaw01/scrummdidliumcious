# Quickstart: SCRUM Poker Session Management

## Goal
Run the SCRUM poker site locally with mock data so you can interact with admin/configuration, session history, session creation from CSV, and live voting behavior.

## Prerequisites
- Python 3.12+
- `uv` installed
- Docker Desktop (optional for Postgres path)

## 1. Install dependencies
```bash
uv sync
```

## 2. Run with mock data (default for this pass)
```bash
export APP_ENV=development
export DATA_BACKEND=inmemory
export FLASK_DEBUG=1
uv run flask --app app run --port 5000
```

Open: `http://localhost:5000`

Expected behavior:
- Session list/history is seeded with mock sessions.
- You can create a new session from CSV and immediately open session detail.
- Real-time events work between two browser windows/tabs connected to the same session.

## 3. Try live collaboration quickly
- Open two browser windows (or one normal + one private window).
- Join the same session in both windows.
- In leader window select an active issue.
- Cast votes in both windows and verify placeholder/vote count sync.
- Reveal votes in leader window and verify all clients update.

## 4. CSV import smoke file
Use a CSV with headers in any order. Required fields:
- `Issue Type` (`Story` or `Bug`)
- `Issue Key`
- `Summary`

Optional fields:
- `Description`
- `Story points`

Example:
```csv
Summary,Issue Key,Issue Type,Description,Story points
As a user I can login,AUTH-101,Story,Login flow,3
Fix timeout on token refresh,AUTH-112,Bug,,
```

## 5. Theme persistence check
- Toggle light/dark mode in UI.
- Refresh and reopen page.
- Confirm selected mode persists.

## 6. Optional Postgres local runtime (for adapter validation)
```bash
docker compose -f docker/docker-compose.yml up -d postgres
export DATA_BACKEND=postgres
export DATABASE_URL=postgresql+psycopg://poker_user:dev_password@localhost:5432/scrum_poker
uv run flask --app app run --port 5000
```

## 7. Test command set
```bash
uv run pytest tests/unit
uv run pytest tests/integration
uv run pytest tests/contract
```

## 8. Formatting and quality gates
```bash
uv run black .
uv run ruff check .
```

## Notes for this iteration
- Persistence is intentionally mock-first so local interaction is immediate.
- Service and repository interfaces should remain stable when replacing in-memory adapters with SQLAlchemy/Postgres adapters later.
