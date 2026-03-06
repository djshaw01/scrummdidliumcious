# scrummdidliumcious
Experimental Scrumm poker and Retro

## Prerequisites

- Python 3.11 or newer
- [`uv`](https://docs.astral.sh/uv/) package manager (`pip install uv` or system install)
- Docker (for local PostgreSQL baseline)

## Getting Started

### 1. Install dependencies

```bash
uv sync
```

### 2. Start the PostgreSQL baseline (optional — not required for the landing page)

```bash
docker compose -f docker/docker-compose.yml up -d postgres
```

### 3. Run the Flask app locally

```bash
uv run flask --app app run --debug
```

Then open [http://localhost:5000/](http://localhost:5000/) in your browser.

### 4. Shutdown and cleanup

Stop the Flask dev server: press **Ctrl+C** in the terminal.

Stop and remove the Docker PostgreSQL container:

```bash
docker compose -f docker/docker-compose.yml down
```

Remove the PostgreSQL data volume (destructive):

```bash
docker compose -f docker/docker-compose.yml down -v
```

## Running Tests

```bash
uv run pytest -q
```

## Code Formatting

Check formatting:

```bash
uv run black --check .
```

Auto-format:

```bash
uv run black .
```

## Building the Container Image

```bash
docker build -f docker/Dockerfile -t scrummdidliumcious:home-landing .
```

## SCRUM Poker Development Workflow

### Start the full stack (Flask + PostgreSQL)

```bash
docker compose -f docker/docker-compose.yml up -d postgres
uv run flask --app app run --debug
```

### Apply database migrations

```bash
uv run alembic upgrade head
```

### Run the targeted SCRUM Poker test suite

```bash
# All poker-related tests
uv run pytest -q tests/unit tests/contract tests/integration

# Single test module
uv run pytest -q tests/unit/test_vote_service.py
```

### CI quality gate (mirrors GitHub Actions)

```bash
uv run black --check .
uv run pytest -q
```

### Auto-format before committing

```bash
uv run black .
```
