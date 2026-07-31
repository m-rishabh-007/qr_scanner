#!/usr/bin/env bash
set -euo pipefail
if [[ $# -ne 1 ]]; then echo "Usage: $0 backup.dump" >&2; exit 2; fi
COMPOSE_FILE="${COMPOSE_FILE:-ops/compose.yml}"
cat "$1" | docker compose -f "$COMPOSE_FILE" exec -T db pg_restore --clean --if-exists -U "${POSTGRES_USER:-reviewflow}" -d "${POSTGRES_DB:-reviewflow}"
