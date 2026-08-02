# ReviewFlow MVP monorepo

Production-oriented implementation baseline for the QR-based review assistant.

## Repository layout

- `backend/` — Django 5.2 LTS, Django REST Framework, PostgreSQL, public customer flow, merchant APIs and Django Admin.
- `mobile/` — Expo React Native TypeScript merchant app.
- `ops/` — Docker Compose, Caddy and deployment/backup scripts.
- `.github/workflows/` — CI, staging and production workflows. Staging and production jobs reference protected GitHub environments.
- `docs/` — architecture, configuration and release notes.

## Product identity and configuration

Most branding and deployment values are environment-driven. The mobile app resolves build-time identity in `mobile/app.config.ts`; the backend reads environment variables from `.env`.

Important: the Android package/application ID can be configured before the first store upload, but changing it later creates a different app. Treat `ANDROID_PACKAGE` as permanent once the Play Console app is created.

## Local start

```bash
cp .env.example .env

docker compose \
  --env-file .env \
  -f ops/compose.yml \
  -f ops/compose.local.yml \
  --profile local \
  config --quiet

docker compose \
  --env-file .env \
  -f ops/compose.yml \
  -f ops/compose.local.yml \
  --profile local \
  up --build -d
```

Then:

- Public site through Caddy: `http://localhost:8080`
- Direct backend development port: `http://localhost:8000`
- Django Admin through Caddy: `http://localhost:8080/admin/`
- API schema through Caddy: `http://localhost:8080/api/schema/`
- Mailpit: `http://localhost:8025`

Create a superuser and seed configurable domains:

```bash
docker compose \
  --env-file .env \
  -f ops/compose.yml \
  -f ops/compose.local.yml \
  --profile local \
  exec backend python manage.py createsuperuser

docker compose \
  --env-file .env \
  -f ops/compose.yml \
  -f ops/compose.local.yml \
  --profile local \
  exec backend python manage.py seed_initial_catalog
```

Inspect service state and raw logs before changing code:

```bash
docker compose \
  --env-file .env \
  -f ops/compose.yml \
  -f ops/compose.local.yml \
  --profile local \
  ps

docker compose \
  --env-file .env \
  -f ops/compose.yml \
  -f ops/compose.local.yml \
  --profile local \
  logs --no-color backend db litellm caddy mailpit
```

Mobile app:

```bash
cd mobile
npm ci --no-audit --no-fund
npm run start
```

## Default business rules

- One merchant account owns one physical location in MVP.
- Registration requires email verification and administrator approval.
- Restaurant, hotel, salon and retail domains are seeded through data, not hard-coded UI.
- Questions and active prompt versions are maintained in Django Admin.
- Customer review generation uses an OpenAI-compatible LiteLLM endpoint.
- Every completed customer receives the same Google path regardless of rating.
- Exactly three drafts are generated: short, natural and detailed.
- Production and staging deployments require GitHub Environment approval.

## Security notes

Never commit `.env`, EAS credentials, Play upload keys or production secrets. CI uses read-only permissions by default and deployment jobs use environment-scoped secrets.
