FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies (production only)
RUN uv sync --no-dev

# Copy application source
COPY app/ ./app/
COPY images/ ./images/

EXPOSE 5000

ENV FLASK_APP=app
ENV FLASK_ENV=production

CMD ["uv", "run", "flask", "--app", "app", "run", "--host", "0.0.0.0", "--port", "5000"]
