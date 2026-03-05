# Scrummdidliumcious — SCRUM Poker

A locally-runnable SCRUM poker web app with real-time collaborative voting,
session history, CSV-based session creation, and admin configuration.

**Stack**: Python 3.12 · Flask · Flask-SocketIO · Jinja2 · SQLAlchemy · PostgreSQL (optional) · Docker

---

## Prerequisites

| Requirement | Version | Install |
|---|---|---|
| **Python** | 3.12+ | `python --version` to verify |
| **[uv](https://docs.astral.sh/uv/getting-started/installation/)** | latest | Required — pip is not supported |
| **Docker Desktop** | latest | Optional — needed for PostgreSQL and container builds |

---

## Quick Start

```bash
# 1. Install all dependencies (runtime + dev)
uv sync

# 2. Copy the environment template
cp .env.example .env

# 3. Start the server
uv run flask --app app run --port 5000
```

Open **http://localhost:5000** — you will see the app skeleton with navigable placeholder pages.

---

## Running Tests

```bash
# Run all tests
uv run pytest

# Unit tests only
uv run pytest tests/unit -v

# Integration tests (available from Stage 2 onwards)
uv run pytest tests/integration -v

# Contract tests (available from Stage 3 onwards)
uv run pytest tests/contract -v

# With coverage report (outputs to terminal)
uv run pytest --cov=app --cov-report=term-missing tests/

# With HTML coverage report
uv run pytest --cov=app --cov-report=html tests/
open htmlcov/index.html

# Run a single test file
uv run pytest tests/unit/test_smoke.py -v

# Run tests matching a keyword
uv run pytest -k "us1" -v
```

---

## Code Quality

```bash
# Format all Python files with black
uv run black .

# Check for lint issues with ruff
uv run ruff check .

# Auto-fix lint issues
uv run ruff check --fix .

# Run both gates together (used in CI)
uv run black . && uv run ruff check .
```

---

## Development Stages

The application is built incrementally. Each stage adds a working slice of
functionality you can run, test, and validate independently before moving on.

---

### Stage 1 — Setup *(current)*

**What works:** Flask app factory, stub routes, navigable skeleton pages in
light and dark mode.

```bash
# Install dependencies
uv sync

# Start the app
uv run flask --app app run --port 5000

# Run Stage 1 smoke tests
uv run pytest tests/unit/test_smoke.py -v
```

**Pages you can open:**

| URL | Page |
|---|---|
| `http://localhost:5000/` | Session history (placeholder) |
| `http://localhost:5000/sessions/new` | New session form (placeholder) |
| `http://localhost:5000/sessions/any-id` | Session detail (placeholder) |
| `http://localhost:5000/admin/` | Admin configuration (placeholder) |

**Verify the stage is working:**
- All four pages load without errors.
- The theme toggle (◐) switches between light and dark mode.
- Theme preference persists across page refreshes.

---

### Stage 2 — Foundational

**What's added:** Domain entities, repository interfaces, in-memory seed
data, SocketIO room helpers, shared base template fully wired, CSS/JS foundations.

```bash
# Start the app (same command)
uv run flask --app app run --port 5000

# Run unit and integration tests
uv run pytest tests/unit tests/integration -v
```

**Verify the stage is working:**
- App starts with seeded in-memory data (teams, sessions visible).
- All pages load without error.
- Browser console shows `connected` SocketIO event after joining a session.

---

### Stage 3 — User Story 1 (MVP): Live Estimation Session

**What's added:** Real-time voting, issue selection and reveal, final
estimate save, and automatic leader reassignment on disconnect.

```bash
# Start the app
uv run flask --app app run --port 5000

# Run US1 tests
uv run pytest -k "us1" -v

# Two-browser manual check:
# 1. Open two browser windows to the same session URL.
# 2. Cast votes in both — verify anonymised placeholders and N/M count sync.
# 3. Reveal in the leader window — verify both windows update simultaneously.
# 4. Close the leader window — verify a new leader is assigned within 2 s.
```

**Verify the stage is working:**
- Participants join and see the same active issue.
- Vote count (`N/M`) updates in real time.
- Leader-only Reveal replaces placeholders with actual cards and shows the average.
- Leader can enter and save a custom estimate.

---

### Stage 4 — User Story 2: Create Session from CSV

**What's added:** CSV upload, session creation form, team name prefill,
inline validation errors.

```bash
# Start the app
uv run flask --app app run --port 5000

# Run US2 tests
uv run pytest -k "us2" -v
```

**Example CSV (`issues.csv`):**

```csv
Summary,Issue Key,Issue Type,Description,Story points
As a user I can log in,AUTH-101,Story,Login flow,3
Fix timeout on token refresh,AUTH-112,Bug,,
```

**Verify the stage is working:**
- Selecting a team pre-fills the session name from the team's most recent session.
- Uploading a CSV with columns in any order imports all valid rows.
- Invalid rows show row-level feedback; valid rows remain importable.
- Submitting redirects to the new session detail page.
- New session appears at the top of history for all viewers.

---

### Stage 5 — User Story 3: Session History

**What's added:** Session list sorted by recency, filter by name/sprint/team,
open any session.

```bash
# Start the app
uv run flask --app app run --port 5000

# Run US3 tests
uv run pytest -k "us3" -v
```

**Verify the stage is working:**
- Entry page lists sessions most-recent first.
- Applying name, sprint, or team filters narrows the list.
- Clicking a session opens its detail page.

---

### Stage 6 — User Story 4: Admin Configuration

**What's added:** Team CRUD, base issue URL configuration, completed session
deletion.

```bash
# Start the app
uv run flask --app app run --port 5000

# Run US4 tests
uv run pytest -k "us4" -v
```

**Verify the stage is working:**
- Adding a team makes it available in the new-session team dropdown.
- Setting a base issue URL turns issue keys into clickable links in session views.
- Deleting a completed session removes it from history immediately.

---

### Stage 7 — Polish & Validation

**What's added:** Browser smoke tests, realtime performance checks, docstring
validation, final quality gates.

```bash
# Full test suite
uv run pytest -v

# With coverage
uv run pytest --cov=app --cov-report=html tests/
open htmlcov/index.html

# Format + lint gate
uv run black . && uv run ruff check .
```

**Verify the stage is working:**
- All tests pass across unit, integration, and contract suites.
- Black and ruff report no issues.
- Session state updates are visible to clients within 2 seconds in ≥95% of interactions.

---

## Optional: PostgreSQL

Skip this section during Stages 1–2. Useful from Stage 3 onwards for adapter
validation.

```bash
# Start just the Postgres container
docker compose -f docker/docker-compose.yml up -d postgres

# Run the app against Postgres
export DATA_BACKEND=postgres
export DATABASE_URL=postgresql+psycopg://poker_user:dev_password@localhost:5432/scrum_poker
uv run flask --app app run --port 5000
```

---

## Optional: Docker Build

```bash
# Build the image
docker build -f docker/Dockerfile -t scrum-poker .

# Run the container (in-memory mode)
docker run -p 5000:5000 -e APP_ENV=development -e DATA_BACKEND=inmemory scrum-poker

# Full stack (app + Postgres) via Compose
docker compose -f docker/docker-compose.yml up --build
```

---

## Environment Variables

See `.env.example` for the full list. Key variables:

| Variable | Default | Description |
|---|---|---|
| `APP_ENV` | `development` | Config class: `development`, `testing`, `postgres` |
| `DATA_BACKEND` | `inmemory` | Storage: `inmemory` (default) or `postgres` |
| `SECRET_KEY` | *(dev key)* | Flask session secret — **change before any shared deploy** |
| `DATABASE_URL` | *(local postgres)* | SQLAlchemy URL (postgres mode only) |
| `FLASK_DEBUG` | `1` | Enable debug mode (development only) |

---

## Project Structure

```
app/
├── __init__.py              # App factory
├── config.py                # Configuration classes (development / testing / postgres)
├── web/
│   ├── routes_admin.py      # Admin page routes
│   ├── routes_sessions.py   # Session, history, and voting routes
│   └── sockets.py           # SocketIO event handlers
├── domain/
│   ├── entities/            # Domain entities (Phase 2)
│   ├── services/            # Business-logic services (Phases 2–6)
│   └── repositories/        # Repository interfaces (Phase 2)
├── infra/
│   ├── repository_inmemory/ # In-memory adapters + seed data (Phase 2)
│   ├── repository_sqlalchemy/ # SQLAlchemy adapters (Phase 2+)
│   └── csv_import/          # CSV parser and validator (Phase 4)
├── templates/
│   ├── shared/base.html     # Base layout with nav and theme toggle
│   ├── admin/               # Admin configuration page
│   ├── history/             # Session history / entry page
│   └── session/             # Session detail and new-session pages
└── static/
    ├── css/styles.css       # Global styles with light/dark theme
    └── js/app.js            # Theme persistence and SocketIO bootstrap

tests/
├── conftest.py              # Shared pytest fixtures
├── unit/                    # Fast, isolated unit tests
├── integration/             # Multi-component and SocketIO flow tests
└── contract/                # API contract validation tests

docker/
├── Dockerfile               # Container image for the app
└── docker-compose.yml       # App + PostgreSQL local stack
```
