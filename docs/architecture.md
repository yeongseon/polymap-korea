# PolyMap Korea Architecture Decisions

## Summary

Issue #1 establishes the v1 monorepo foundation for a Korean local election voter information service focused on reliability, traceable source evidence, and fast local development.

## Confirmed Decisions

1. **PostgreSQL only for v1**
   - Neo4j is excluded.
   - Relationship-heavy views are exposed as graph-shaped DTOs from PostgreSQL-backed services.

2. **Docker Compose only**
   - Kubernetes is out of scope for v1.
   - Infrastructure services run via Compose profiles for local and CI-friendly development.

3. **FastAPI OpenAPI as contract source of truth**
   - `packages/contracts` stores generated TypeScript artifacts from the backend schema.
   - API contracts flow from backend definitions, not a separate schema package.

4. **Language-specific shared code**
   - Shared Python utilities live in `pipeline/common`.
   - Cross-language shared packages are intentionally avoided for now.

5. **Tooling choices**
   - TypeScript uses `pnpm` workspaces.
   - Python uses `uv` with per-project `pyproject.toml` files.
   - Monorepo task runners such as Turborepo and Nx are intentionally not introduced.

6. **Pipeline orchestration**
   - Prefect is the orchestration layer for ingestion, normalization, and publishing workflows.

7. **Local runtime model**
   - Next.js, FastAPI, and pipeline code can run on the host machine for development.
   - Docker Compose `core` profile includes all application services alongside infrastructure dependencies.

## Repository Layout

- `apps/web`: Next.js 14 App Router frontend
- `apps/api`: FastAPI backend and OpenAPI source
- `packages/contracts`: generated TypeScript contracts
- `packages/ontology`: RDF/SHACL/JSON-LD assets
- `pipeline`: source adapters, normalization, and publish flows
- `infra/docker`: reserved for future Docker-related assets

## Compose Profiles

- `core`: PostgreSQL, MinIO, Prefect server, API, Web, Pipeline worker
- `search`: OpenSearch
- `orchestrator`: Prefect server
- `monitoring`: Prometheus, Grafana, postgres-exporter, node-exporter
- `full`: everything above
