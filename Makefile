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

MAX_LINE_LENGHT := $$(cat "`git rev-parse --show-toplevel`/setup.cfg" | grep "max-line-length" | grep -Eo '[[:digit:]]+' | head -n 1)
LOCAL_DOCKER_COMPOSE = "deployment/dev/docker-compose.yml"
PRODUCTION_DOCKER_COMPOSE = "deployment/production/docker-compose.yml"
PROJECT_NAME = 'orderflow'

include .env
include .env

lint:
> isort -l $(MAX_LINE_LENGHT) orderflow
> black -l $(MAX_LINE_LENGHT) .
> flake8 .
.PHONY: lint

local-stack-up:
>	docker-compose -f $(LOCAL_DOCKER_COMPOSE) -p $(PROJECT_NAME) up --build
.PHONY: local-stack-up

production-stack-up:
>	docker-compose -f $(PRODUCTION_DOCKER_COMPOSE) -p $(PROJECT_NAME) up --build
.PHONY: production-stack-up

local-stack-down:
>	docker-compose -f $(LOCAL_DOCKER_COMPOSE) -p $(PROJECT_NAME) down
.PHONY: local-stack-down

production-stack-down:
>	docker-compose -f $(PRODUCTION_DOCKER_COMPOSE) -p $(PROJECT_NAME) down
.PHONY: production-stack-down

r:
>	docker-compose -f $(LOCAL_DOCKER_COMPOSE) -p $(PROJECT_NAME) restart web
.PHONY: r

python-shell:
>	docker-compose -f $(LOCAL_DOCKER_COMPOSE) -p $(PROJECT_NAME) exec web orderflow/manage.py shell
.PHONY: python-shell

local-bash:
>	docker-compose -f $(LOCAL_DOCKER_COMPOSE) -p $(PROJECT_NAME) exec web bash
.PHONY: local-bash

production-bash:
>	docker-compose -f $(PRODUCTION_DOCKER_COMPOSE) -p $(PROJECT_NAME) exec web bash
.PHONY: production-bash

local-psql:
> export `cat .env`
>	docker-compose -f $(LOCAL_DOCKER_COMPOSE) -p $(PROJECT_NAME) exec db psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)
.PHONY: local-psql

production-psql:
> export `cat .env`
>	docker-compose -f $(PRODUCTION_DOCKER_COMPOSE) -p $(PROJECT_NAME) exec db psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)
.PHONY: production-psql

local-migrate:
>	docker-compose -f $(LOCAL_DOCKER_COMPOSE) -p $(PROJECT_NAME) exec web orderflow/manage.py migrate
.PHONY: local-migrate

production-migrate:
>	docker-compose -f $(PRODUCTION_DOCKER_COMPOSE) -p $(PROJECT_NAME) exec web orderflow/manage.py migrate
.PHONY: production-migrate

makemigrations:
>	docker-compose -f $(LOCAL_DOCKER_COMPOSE) -p $(PROJECT_NAME) exec web orderflow/manage.py makemigrations
.PHONY: makemigrations

rebuild-web-img:
>	docker-compose -f $(LOCAL_DOCKER_COMPOSE) -p $(PROJECT_NAME) build web
>	docker-compose -f $(LOCAL_DOCKER_COMPOSE) -p $(PROJECT_NAME) rm -f web
>	docker-compose -f $(LOCAL_DOCKER_COMPOSE) -p $(PROJECT_NAME) up -d web
.PHONY: rebuild-web-img


show-net-conf:
>	docker-compose -f $(LOCAL_DOCKER_COMPOSE) -p $(PROJECT_NAME) ps  | head -n 2 | tail -n 1 | awk '{printf $$1}' | xargs docker inspect | jq '.[].NetworkSettings.Networks'
.PHONY: show-net-conf


test:
>  docker-compose -f $(LOCAL_DOCKER_COMPOSE) -p $(PROJECT_NAME) exec web \
>  sh -lc 'cd /app; \
>  set -a; [ -f .env ] && . ./.env; set +a; \
>  export DJANGO_SETTINGS_MODULE=$${DJANGO_SETTINGS_MODULE:-orderflow.settings.local}; \
>  export PYTHONPATH=/app:$${PYTHONPATH}; \
>  pytest'
.PHONY: test
