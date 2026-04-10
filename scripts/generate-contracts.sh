#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_DIR="$ROOT_DIR/apps/api"
OPENAPI_FILE="${TMPDIR:-/tmp}/polymap-openapi.json"
WEB_OUTPUT_FILE="$ROOT_DIR/apps/web/src/lib/generated-types.ts"
CONTRACTS_OUTPUT_FILE="$ROOT_DIR/packages/contracts/src/index.ts"
HEADER='// Auto-generated from OpenAPI spec. Do not edit manually. Regenerate: scripts/generate-contracts.sh'

for cmd in pnpm python3; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    printf '%s is required to generate contracts\n' "$cmd" >&2
    exit 1
  fi
done

export PATH="$HOME/.local/bin:$PATH"

mkdir -p "$(dirname "$WEB_OUTPUT_FILE")" "$(dirname "$CONTRACTS_OUTPUT_FILE")"

(cd "$API_DIR" && PYTHONPATH="$API_DIR/src" python3 -c 'import json; from polymap_api.main import app; print(json.dumps(app.openapi(), ensure_ascii=False, indent=2))' > "$OPENAPI_FILE")

(cd "$ROOT_DIR" && pnpm --filter web exec openapi-typescript "$OPENAPI_FILE" -o "$WEB_OUTPUT_FILE")

WEB_OUTPUT_FILE="$WEB_OUTPUT_FILE" CONTRACTS_OUTPUT_FILE="$CONTRACTS_OUTPUT_FILE" HEADER="$HEADER" python3 <<'PY'
from pathlib import Path
import os

header = os.environ["HEADER"]
web_output = Path(os.environ["WEB_OUTPUT_FILE"])
contracts_output = Path(os.environ["CONTRACTS_OUTPUT_FILE"])

generated = web_output.read_text(encoding="utf-8").lstrip("\ufeff")
content = f"{header}\n\n{generated}"

web_output.write_text(content, encoding="utf-8")
contracts_output.write_text(content, encoding="utf-8")
PY

printf 'Generated TypeScript contracts at %s\n' "$WEB_OUTPUT_FILE"
printf 'Generated TypeScript contracts at %s\n' "$CONTRACTS_OUTPUT_FILE"
