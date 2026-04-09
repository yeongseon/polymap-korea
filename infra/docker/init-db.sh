#!/usr/bin/env bash
# Creates additional databases needed by services.
# This script is mounted into postgres via docker-entrypoint-initdb.d/
# and runs automatically on first container start.

set -euo pipefail

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE prefect;
    GRANT ALL PRIVILEGES ON DATABASE prefect TO $POSTGRES_USER;
EOSQL
