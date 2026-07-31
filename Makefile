.PHONY: up down logs test lint migrate seed mobile-install
up:
	docker compose -f ops/compose.yml up --build

down:
	docker compose -f ops/compose.yml down

logs:
	docker compose -f ops/compose.yml logs -f backend

test:
	docker compose -f ops/compose.yml run --rm backend pytest

lint:
	docker compose -f ops/compose.yml run --rm backend ruff check .

migrate:
	docker compose -f ops/compose.yml exec backend python manage.py migrate

seed:
	docker compose -f ops/compose.yml exec backend python manage.py seed_initial_catalog

mobile-install:
	cd mobile && npm install && npx expo install --fix
