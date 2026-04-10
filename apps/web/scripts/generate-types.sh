#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEB_DIR="$(dirname "$SCRIPT_DIR")"
CONTRACTS_DIR="$WEB_DIR/../../packages/contracts"

API_URL="${POLYMAP_API_URL:-http://localhost:8000}"
OPENAPI_URL="$API_URL/openapi.json"

echo "Fetching OpenAPI spec from $OPENAPI_URL..."
SPEC=$(curl -sf "$OPENAPI_URL") || {
  echo "ERROR: Could not reach $OPENAPI_URL"
  echo "Make sure the API server is running: uvicorn polymap_api.main:app"
  exit 1
}

echo "$SPEC" | npx openapi-typescript - -o "$WEB_DIR/src/lib/generated-types.ts"
echo "$SPEC" | npx openapi-typescript - -o "$CONTRACTS_DIR/src/index.ts"

echo "Types generated successfully."
echo "  -> $WEB_DIR/src/lib/generated-types.ts"
echo "  -> $CONTRACTS_DIR/src/index.ts"
