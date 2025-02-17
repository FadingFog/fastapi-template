COMPOSE_FILE ?= app-docker/docker-compose.yaml
SERVICE_NAME ?= fastapi-template
SERVICE_DB ?= fastapi-template-db
ALEMBIC_INI_PATH ?= app/db/migrations/alembic.ini


include .env


.PHONY: up build down generate upgrade downgrade ruff-fix format lint


up:
	docker compose -f ${COMPOSE_FILE} up ${SERVICE_NAME} ${SERVICE_DB} --remove-orphans

build:
	docker compose -f ${COMPOSE_FILE} build

down:
	docker compose -f ${COMPOSE_FILE} down ${SERVICE_NAME} --remove-orphans

generate:
	alembic -c ${ALEMBIC_INI_PATH} revision --autogenerate -m "$(m)"

upgrade:
	alembic -c ${ALEMBIC_INI_PATH} upgrade $(if $(v),$(v),head)

downgrade:
	alembic -c ${ALEMBIC_INI_PATH} downgrade ${n}

ruff-fix:
	ruff check --fix .

format:
	ruff format .

lint: format ruff-fix
	pre-commit run --all-files
