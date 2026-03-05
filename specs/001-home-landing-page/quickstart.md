# Quickstart: Home Landing Page Foundation

## Prerequisites
- Python 3.11+
- `uv` installed
- Docker (for local PostgreSQL baseline)

## 1. Install dependencies
```bash
uv sync
```

## 2. Start PostgreSQL baseline (Docker)
```bash
docker compose -f docker/docker-compose.yml up -d postgres
```

## 3. Run Flask app locally
```bash
uv run flask --app app run --debug
```

## 4. Validate landing page behavior
1. Open `http://localhost:5000/`.
2. Confirm visible page title is `SCRUMMDidliumcious`.
3. Confirm logo uses `images/scrumm_logo.svg` in top-left placement.
4. Confirm logo height is 100em and aspect ratio is preserved.
5. Check desktop and mobile viewport behavior.

## 5. Run tests
```bash
uv run pytest -q
```

## 6. Run formatting check
```bash
uv run black --check .
```

## 7. Build container image
```bash
docker build -f docker/Dockerfile -t scrummdidliumcious:home-landing .
```
