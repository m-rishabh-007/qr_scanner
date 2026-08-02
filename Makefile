COMPOSE_LOCAL = docker compose --env-file .env -f ops/compose.yml -f ops/compose.local.yml --profile local

.PHONY: compose-config up down logs test lint migrate seed mobile-install

compose-config:
	$(COMPOSE_LOCAL) config --quiet

up:
	$(COMPOSE_LOCAL) up --build

down:
	$(COMPOSE_LOCAL) down

logs:
	$(COMPOSE_LOCAL) logs -f backend db litellm caddy mailpit

test:
	$(COMPOSE_LOCAL) run --rm --no-deps \
		-e RUN_MIGRATIONS=false \
		-e COLLECT_STATIC=false \
		-e DJANGO_SETTINGS_MODULE=config.settings.test \
		backend pytest

lint:
	$(COMPOSE_LOCAL) run --rm --no-deps \
		-e RUN_MIGRATIONS=false \
		-e COLLECT_STATIC=false \
		backend ruff check .

migrate:
	$(COMPOSE_LOCAL) exec backend python manage.py migrate

seed:
	$(COMPOSE_LOCAL) exec backend python manage.py seed_initial_catalog

mobile-install:
	cd mobile && npm ci --no-audit --no-fund
