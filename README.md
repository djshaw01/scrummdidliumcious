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
