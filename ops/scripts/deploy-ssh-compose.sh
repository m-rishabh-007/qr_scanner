#!/usr/bin/env bash
set -euo pipefail
: "${DEPLOY_HOST:?DEPLOY_HOST is required}"
: "${DEPLOY_USER:?DEPLOY_USER is required}"
: "${DEPLOY_PATH:?DEPLOY_PATH is required}"
: "${BACKEND_IMAGE:?BACKEND_IMAGE is required}"
: "${IMAGE_TAG:?IMAGE_TAG is required}"
ssh -o StrictHostKeyChecking=accept-new "$DEPLOY_USER@$DEPLOY_HOST" bash -s -- "$DEPLOY_PATH" "$BACKEND_IMAGE" "$IMAGE_TAG" <<'REMOTE'
set -euo pipefail
DEPLOY_PATH="$1" BACKEND_IMAGE="$2" IMAGE_TAG="$3"
cd "$DEPLOY_PATH"
export BACKEND_IMAGE IMAGE_TAG
docker compose -f ops/compose.yml pull backend
docker compose -f ops/compose.yml run --rm -e RUN_MIGRATIONS=false -e COLLECT_STATIC=false backend python manage.py migrate --noinput
docker compose -f ops/compose.yml up -d --no-deps backend
docker compose -f ops/compose.yml up -d caddy
for _ in $(seq 1 30); do
  if docker compose -f ops/compose.yml exec -T backend python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/', timeout=2)"; then exit 0; fi
  sleep 2
done
exit 1
REMOTE
