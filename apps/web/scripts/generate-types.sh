#!/usr/bin/env bash
set -euo pipefail

cat <<'EOF'
PolyMap Korea frontend type generation

Run from apps/web after the FastAPI backend is serving OpenAPI locally:

  curl http://localhost:8000/openapi.json | npx openapi-typescript - -o src/lib/generated-types.ts

This repository is currently in static demo mode, so handwritten compatibility
types still live in src/lib/types.ts. Regenerate src/lib/generated-types.ts when
backend contracts change and migrate imports incrementally.
EOF
