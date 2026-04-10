FROM python:3.12-slim AS builder

ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_LINK_MODE=copy

WORKDIR /workspace

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir uv

COPY packages/ontology/pyproject.toml packages/ontology/pyproject.toml
COPY packages/ontology/src packages/ontology/src
COPY apps/api/pyproject.toml apps/api/pyproject.toml
COPY apps/api/src apps/api/src

RUN python -m venv /opt/venv \
    && printf '[tool.uv.workspace]\nmembers = ["apps/api", "packages/ontology"]\n\n[tool.uv.sources]\npolymap-ontology = { workspace = true }\n' > pyproject.toml \
    && uv sync --project apps/api --no-dev --no-editable

FROM python:3.12-slim AS runtime

ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY apps/api/alembic.ini ./alembic.ini
COPY apps/api/alembic ./alembic

RUN adduser --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /app /opt/venv

USER appuser

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && exec uvicorn polymap_api.main:app --host 0.0.0.0 --port 8000"]
