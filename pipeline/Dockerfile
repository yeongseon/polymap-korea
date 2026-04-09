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
COPY pipeline/pyproject.toml pipeline/pyproject.toml
COPY pipeline/common pipeline/common
COPY pipeline/flows pipeline/flows
COPY pipeline/normalization pipeline/normalization
COPY pipeline/publish pipeline/publish
COPY pipeline/sources pipeline/sources
COPY pipeline/taxonomy pipeline/taxonomy

RUN python -m venv /opt/venv \
    && printf '[tool.uv.workspace]\nmembers = ["pipeline", "packages/ontology"]\n\n[tool.uv.sources]\npolymap-ontology = { workspace = true }\n' > pyproject.toml \
    && uv sync --project pipeline --no-dev --no-editable

FROM python:3.12-slim AS runtime

ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv

CMD ["prefect", "worker", "start", "--pool", "polymap-pool"]
