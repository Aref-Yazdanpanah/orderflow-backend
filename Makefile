SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

ifeq ($(origin .RECIPEPREFIX), undefined)
  $(error This Make does not support .RECIPEPREFIX. Please use GNU Make 4.0 or later)
endif
.RECIPEPREFIX = >

# --- Compose auto-detect (v2: `docker compose`, v1: `docker-compose`) ---
COMPOSE := $(shell if docker compose version >/dev/null 2>&1; then echo "docker compose"; else echo "docker-compose"; fi)

MAX_LINE_LENGHT := $$(cat "`git rev-parse --show-toplevel`/setup.cfg" | grep "max-line-length" | grep -Eo '[[:digit:]]+' | head -n 1)
LOCAL_DOCKER_COMPOSE = "deployment/dev/docker-compose.yml"
PRODUCTION_DOCKER_COMPOSE = "deployment/production/docker-compose.yml"
PROJECT_NAME = 'orderflow'

# Load environment (OK if missing)
-include .env

# -----------------------------
# Quality / Formatting
# -----------------------------
lint:
> isort -l $(MAX_LINE_LENGHT) orderflow
> black -l $(MAX_LINE_LENGHT) .
> flake8 .
.PHONY: lint

# -----------------------------
# Dev stack controls
# -----------------------------
local-stack-up:
>	$(COMPOSE) -f $(LOCAL_DOCKER_COMPOSE) -p $(PROJECT_NAME) up --build
.PHONY: local-stack-up

local-stack-down:
>	$(COMPOSE) -f $(LOCAL_DOCKER_COMPOSE) -p $(PROJECT_NAME) down
.PHONY: local-stack-down

r:
>	$(COMPOSE) -f $(LOCAL_DOCKER_COMPOSE) -p $(PROJECT_NAME) restart web
.PHONY: r

local-bash:
>	$(COMPOSE) -f $(LOCAL_DOCKER_COMPOSE) -p $(PROJECT_NAME) exec web bash
.PHONY: local-bash

python-shell:
>	$(COMPOSE) -f $(LOCAL_DOCKER_COMPOSE) -p $(PROJECT_NAME) exec web orderflow/manage.py shell
.PHONY: python-shell

local-psql:
> export `cat .env`
>	$(COMPOSE) -f $(LOCAL_DOCKER_COMPOSE) -p $(PROJECT_NAME) exec db psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)
.PHONY: local-psql

local-migrate:
>	$(COMPOSE) -f $(LOCAL_DOCKER_COMPOSE) -p $(PROJECT_NAME) exec web orderflow/manage.py migrate
.PHONY: local-migrate

makemigrations:
>	$(COMPOSE) -f $(LOCAL_DOCKER_COMPOSE) -p $(PROJECT_NAME) exec web orderflow/manage.py makemigrations
.PHONY: makemigrations

rebuild-web-img:
>	$(COMPOSE) -f $(LOCAL_DOCKER_COMPOSE) -p $(PROJECT_NAME) build web
>	$(COMPOSE) -f $(LOCAL_DOCKER_COMPOSE) -p $(PROJECT_NAME) rm -f web
>	$(COMPOSE) -f $(LOCAL_DOCKER_COMPOSE) -p $(PROJECT_NAME) up -d web
.PHONY: rebuild-web-img

show-net-conf:
>	$(COMPOSE) -f $(LOCAL_DOCKER_COMPOSE) -p $(PROJECT_NAME) ps  | head -n 2 | tail -n 1 | awk '{printf $$1}' | xargs docker inspect | jq '.[].NetworkSettings.Networks'
.PHONY: show-net-conf

# -----------------------------
# Prod stack controls
# -----------------------------
production-stack-up:
>	$(COMPOSE) -f $(PRODUCTION_DOCKER_COMPOSE) -p $(PROJECT_NAME) up --build
.PHONY: production-stack-up

production-stack-down:
>	$(COMPOSE) -f $(PRODUCTION_DOCKER_COMPOSE) -p $(PROJECT_NAME) down
.PHONY: production-stack-down

production-bash:
>	$(COMPOSE) -f $(PRODUCTION_DOCKER_COMPOSE) -p $(PROJECT_NAME) exec web bash
.PHONY: production-bash

production-psql:
> export `cat .env`
>	$(COMPOSE) -f $(PRODUCTION_DOCKER_COMPOSE) -p $(PROJECT_NAME) exec db psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)
.PHONY: production-psql

production-migrate:
>	$(COMPOSE) -f $(PRODUCTION_DOCKER_COMPOSE) -p $(PROJECT_NAME) exec web orderflow/manage.py migrate
.PHONY: production-migrate

# -----------------------------
# Tests
# -----------------------------
test:
>  $(COMPOSE) -f $(LOCAL_DOCKER_COMPOSE) -p $(PROJECT_NAME) exec web \
>  sh -lc 'cd /app; \
>  set -a; [ -f .env ] && . ./.env; set +a; \
>  export DJANGO_SETTINGS_MODULE=$${DJANGO_SETTINGS_MODULE:-orderflow.settings.local}; \
>  export PYTHONPATH=/app:$${PYTHONPATH}; \
>  pytest'
.PHONY: test
