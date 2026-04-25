.PHONY: help build up down restart logs ps shell test cov lint format check api

DOCKER_COMPOSE ?= docker compose
APP_SERVICE ?= app
UV_RUN_TASK ?= uv run task

help:
	@printf "\nTargets disponíveis:\n\n"
	@printf "  make build    Builda a imagem do projeto\n"
	@printf "  make up       Sobe os containers em background\n"
	@printf "  make down     Derruba os containers\n"
	@printf "  make restart  Reinicia os containers\n"
	@printf "  make logs     Exibe os logs do compose\n"
	@printf "  make ps       Lista os containers do compose\n"
	@printf "  make shell    Abre um shell no container app\n"
	@printf "  make api      Sobe a API FastAPI na porta 8000\n"
	@printf "  make test     Executa os testes\n"
	@printf "  make cov      Executa os testes com coverage xml\n"
	@printf "  make lint     Executa o lint\n"
	@printf "  make format   Formata o código\n"
	@printf "  make check    Executa lint, mypy e testes\n\n"

build:
	$(DOCKER_COMPOSE) build

up:
	$(DOCKER_COMPOSE) up -d

down:
	$(DOCKER_COMPOSE) down

restart:
	$(DOCKER_COMPOSE) down
	$(DOCKER_COMPOSE) up -d

logs:
	$(DOCKER_COMPOSE) logs -f

ps:
	$(DOCKER_COMPOSE) ps

shell:
	$(DOCKER_COMPOSE) exec $(APP_SERVICE) bash

api:
	$(DOCKER_COMPOSE) exec $(APP_SERVICE) $(UV_RUN_TASK) api

test:
	$(DOCKER_COMPOSE) exec $(APP_SERVICE) $(UV_RUN_TASK) test

cov:
	$(DOCKER_COMPOSE) exec $(APP_SERVICE) $(UV_RUN_TASK) cov

lint:
	$(DOCKER_COMPOSE) exec $(APP_SERVICE) $(UV_RUN_TASK) lint

format:
	$(DOCKER_COMPOSE) exec $(APP_SERVICE) $(UV_RUN_TASK) format

check:
	$(DOCKER_COMPOSE) exec $(APP_SERVICE) $(UV_RUN_TASK) check
