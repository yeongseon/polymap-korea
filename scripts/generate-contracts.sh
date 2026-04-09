#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_DIR="$ROOT_DIR/apps/api"
OPENAPI_FILE="$API_DIR/openapi.json"
OUTPUT_FILE="$ROOT_DIR/packages/contracts/src/index.ts"

for cmd in pnpm uv; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    printf '%s is required to generate contracts\n' "$cmd" >&2
    exit 1
  fi
done

mkdir -p "$(dirname "$OUTPUT_FILE")"

(cd "$API_DIR" && uv run python -c 'import json; from polymap_api.main import app; print(json.dumps(app.openapi(), ensure_ascii=False, indent=2))' > "$OPENAPI_FILE")

(cd "$ROOT_DIR" && pnpm dlx openapi-typescript@7.6.1 "$OPENAPI_FILE" --output "$OUTPUT_FILE")

printf 'Generated TypeScript contracts at %s\n' "$OUTPUT_FILE"
