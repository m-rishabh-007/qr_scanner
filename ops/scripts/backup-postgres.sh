#!/usr/bin/env bash
set -euo pipefail
COMPOSE_FILE="${COMPOSE_FILE:-ops/compose.yml}"
BACKUP_DIR="${BACKUP_DIR:-./backups}"
RETENTION_DAYS="${RETENTION_DAYS:-35}"
mkdir -p "$BACKUP_DIR"
filename="$BACKUP_DIR/reviewflow-$(date -u +%Y%m%dT%H%M%SZ).dump"
docker compose -f "$COMPOSE_FILE" exec -T db pg_dump -U "${POSTGRES_USER:-reviewflow}" -d "${POSTGRES_DB:-reviewflow}" -Fc > "$filename"
find "$BACKUP_DIR" -type f -name 'reviewflow-*.dump' -mtime "+$RETENTION_DAYS" -delete
printf 'Backup written to %s\n' "$filename"
