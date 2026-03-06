# Quickstart: SCRUM Poker Voting System

## Prerequisites
- Python 3.11+
- `uv`
- Docker

## 1. Install dependencies
```bash
uv sync
```

## 2. Start PostgreSQL baseline
```bash
docker compose -f docker/docker-compose.yml up -d postgres
```

## 3. Run database migrations
```bash
uv run alembic upgrade head
```

## 4. Start application
```bash
uv run flask --app app run --debug
```

## 5. Validate core flow manually
1. Open `http://localhost:5000/`.
2. Navigate to SCRUM poker entry from home navigation.
3. Create a session with valid CSV containing `Issue Type`, `Issue Key`, `Summary`.
4. Open the same session in two browser windows and join as separate participants.
5. Cast votes and confirm `All votes N/M` updates in near real-time.
6. Reveal votes as leader and verify numeric average behavior.
7. Save a custom estimate and verify the issue card updates.
8. Toggle light/dark theme and confirm persistence after browser restart.

## 6. Run focused tests
```bash
uv run pytest -q tests/unit tests/contract tests/integration
```

## 7. Validate performance targets
```bash
uv run pytest -q tests/integration/test_scrum_poker_performance.py
```

## 8. Enforce formatting
```bash
uv run black --check .
```

## 9. Build delivery image
```bash
docker build -f docker/Dockerfile -t scrummdidliumcious:scrum-poker .
```

## Troubleshooting
- CSV rejected quickly: verify required headers are exact (`Issue Type`, `Issue Key`, `Summary`).
- Missing issue links: set `base_url_for_issues` in admin configuration.
- Real-time delay: verify WebSocket endpoint is connected and PostgreSQL container is healthy.