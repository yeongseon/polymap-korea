#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    printf 'Missing required command: %s\n' "$1" >&2
    exit 1
  fi
}

require_command uv
require_command pnpm
require_command docker

if [ ! -f "$ROOT_DIR/.env" ]; then
  cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
  printf 'Created .env from .env.example\n'
fi

printf 'Syncing API dependencies with uv...\n'
(cd "$ROOT_DIR/apps/api" && uv sync --all-extras)

printf 'Syncing pipeline dependencies with uv...\n'
(cd "$ROOT_DIR/pipeline" && uv sync --all-extras)

printf 'Installing frontend dependencies with pnpm...\n'
(cd "$ROOT_DIR" && pnpm install)

printf 'Setup complete. Start infrastructure with: make dev-infra\n'
