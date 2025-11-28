.PHONY: up down logs shell-backend shell-frontend test lint format reset help

# Default target
help:
	@echo "Cradle Development Commands"
	@echo ""
	@echo "  make up              Start all services in background"
	@echo "  make up-attached     Start all services with logs attached"
	@echo "  make down            Stop all services"
	@echo "  make logs            Tail logs from all services"
	@echo "  make logs-backend    Tail backend logs only"
	@echo "  make logs-frontend   Tail frontend logs only"
	@echo ""
	@echo "  make shell-backend   Open shell in backend container"
	@echo "  make shell-frontend  Open shell in frontend container"
	@echo "  make shell-db        Open psql shell"
	@echo ""
	@echo "  make test            Run backend tests"
	@echo "  make lint            Run linters"
	@echo "  make format          Format code"
	@echo ""
	@echo "  make reset           Stop services and remove volumes"
	@echo "  make rebuild         Rebuild all containers"

# Service management
up:
	docker compose up -d

up-attached:
	docker compose up

down:
	docker compose down

logs:
	docker compose logs -f

logs-backend:
	docker compose logs -f backend

logs-frontend:
	docker compose logs -f frontend

# Shell access
shell-backend:
	docker compose exec backend /bin/bash

shell-frontend:
	docker compose exec frontend /bin/sh

shell-db:
	docker compose exec postgres psql -U cradle -d cradle

# Development
test:
	docker compose exec backend bash -c "PYTHONPATH=/app pytest -v"

lint:
	docker compose exec backend ruff check app/

format:
	docker compose exec backend ruff check --fix app/
	docker compose exec backend ruff format app/

# Cleanup
reset:
	docker compose down -v
	docker compose up -d

rebuild:
	docker compose down
	docker compose build --no-cache
	docker compose up -d
