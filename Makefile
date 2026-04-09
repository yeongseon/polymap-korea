.PHONY: help setup dev-infra api web pipeline lint test

help:
	@echo "폴리맵 코리아 개발 명령어"
	@echo ""
	@echo "  make setup        - 전체 개발 환경 설정"
	@echo "  make dev-infra    - 인프라 서비스 시작 (PostgreSQL, Redis, MinIO)"
	@echo "  make dev-search   - 검색 서비스 추가 시작 (OpenSearch)"
	@echo "  make api          - API 서버 시작"
	@echo "  make web          - 웹 프론트엔드 시작"
	@echo "  make lint         - 전체 린트 실행"
	@echo "  make test         - 전체 테스트 실행"

setup:
	cd apps/api && uv sync --all-extras
	cd pipeline && uv sync --all-extras
	pnpm install

dev-infra:
	docker compose --profile core up -d

dev-search:
	docker compose --profile search up -d

dev-full:
	docker compose --profile full up -d

api:
	cd apps/api && uv run uvicorn polymap_api.main:app --reload --host 0.0.0.0 --port 8000

web:
	cd apps/web && pnpm dev

lint:
	cd apps/api && uv run ruff check src/ tests/
	cd pipeline && uv run ruff check .
	cd apps/web && pnpm lint

test:
	cd apps/api && uv run pytest
	cd pipeline && uv run pytest

test-api:
	cd apps/api && uv run pytest -v

format:
	cd apps/api && uv run ruff format src/ tests/
	cd pipeline && uv run ruff format .
