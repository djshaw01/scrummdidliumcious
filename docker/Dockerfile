FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml README.md ./
RUN uv sync --frozen --no-dev || uv sync --no-dev

COPY app ./app

EXPOSE 5000

CMD ["uv", "run", "flask", "--app", "app", "run", "--host", "0.0.0.0", "--port", "5000"]
