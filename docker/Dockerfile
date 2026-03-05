# ---- build stage ----
FROM python:3.12-slim AS base

WORKDIR /app

# Install uv from the official image — avoids pip for package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project metadata and install runtime dependencies only
COPY pyproject.toml ./
RUN uv sync --no-dev --no-install-project

# Copy application source
COPY app/ ./app/

# ---- runtime config ----
EXPOSE 5000

ENV FLASK_APP=app
ENV APP_ENV=development
ENV DATA_BACKEND=inmemory

# Use Flask development server — replace with a production ASGI/WSGI runner for production
CMD ["uv", "run", "flask", "--app", "app", "run", "--host", "0.0.0.0", "--port", "5000"]
