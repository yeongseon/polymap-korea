#!/usr/bin/env bash

set -euo pipefail

: "${PGHOST:?PGHOST is required}"
: "${PGUSER:?PGUSER is required}"
: "${PGDATABASE:?PGDATABASE is required}"
: "${BACKUP_DIR:?BACKUP_DIR is required}"

timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
backup_file="${BACKUP_DIR}/${PGDATABASE}_${timestamp}.dump"

mkdir -p "${BACKUP_DIR}"

if ! pg_dump --format=custom --file="${backup_file}" --host="${PGHOST}" --username="${PGUSER}" "${PGDATABASE}"; then
  exit 1
fi

if ! find "${BACKUP_DIR}" -type f -name "${PGDATABASE}_*.dump" -mtime +30 -delete; then
  exit 1
fi
