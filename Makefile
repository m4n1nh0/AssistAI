.PHONY: help start stop build generate-openapi

help:
	@echo "Usage: make <target>"
	@echo "Targets: setup-backend-env start stop build generate-openapi validate-rag"

setup-backend-env:
	@echo "Create backend virtual environment and install dependencies"
	@bash scripts/setup_backend_env.sh

start:
	@echo "Start services via Docker Compose"
	@docker compose up -d --build

stop:
	@echo "Stop services"
	@docker compose down

build:
	@echo "Build all images"
	@docker compose build

generate-openapi:
	@python3 scripts/generate_openapi.py

validate-rag:
	@python3 scripts/validate_rag.py
