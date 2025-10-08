# Makefile for AI Product Manager Agent
# Common development commands

.PHONY: help install dev-install clean test lint format run db-up db-down db-reset docker-up docker-down

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

## help: Display this help message
help:
	@echo "$(BLUE)AI Product Manager Agent - Available Commands$(NC)"
	@echo ""
	@grep -E '^## ' $(MAKEFILE_LIST) | sed 's/^## /  /' | column -t -s ':'

## install: Install production dependencies
install:
	@echo "$(GREEN)Installing production dependencies...$(NC)"
	pip install -r requirements.txt

## dev-install: Install development dependencies
dev-install:
	@echo "$(GREEN)Installing development dependencies...$(NC)"
	pip install -r requirements-dev.txt

## clean: Remove Python cache and build artifacts
clean:
	@echo "$(YELLOW)Cleaning up...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	rm -rf .pytest_cache htmlcov .mypy_cache build dist *.egg-info

## test: Run all tests
test:
	@echo "$(GREEN)Running tests...$(NC)"
	pytest tests/ -v

## test-golden: Run golden tests only
test-golden:
	@echo "$(GREEN)Running golden tests...$(NC)"
	pytest tests/golden/ -v -m golden

## test-unit: Run unit tests only
test-unit:
	@echo "$(GREEN)Running unit tests...$(NC)"
	pytest tests/unit/ -v

## test-cov: Run tests with coverage report
test-cov:
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	pytest tests/ --cov=src --cov-report=html --cov-report=term

## lint: Run linters (flake8, mypy)
lint:
	@echo "$(GREEN)Running linters...$(NC)"
	flake8 src/ tests/
	mypy src/

## format: Format code with black and isort
format:
	@echo "$(GREEN)Formatting code...$(NC)"
	black src/ tests/
	isort src/ tests/

## format-check: Check code formatting without making changes
format-check:
	@echo "$(GREEN)Checking code formatting...$(NC)"
	black --check src/ tests/
	isort --check-only src/ tests/

## run: Run the agent in interactive mode
run:
	@echo "$(GREEN)Starting AI Product Manager Agent...$(NC)"
	python src/main.py --interactive

## db-up: Start PostgreSQL database
db-up:
	@echo "$(GREEN)Starting PostgreSQL database...$(NC)"
	docker-compose up -d postgres redis

## db-down: Stop PostgreSQL database
db-down:
	@echo "$(YELLOW)Stopping database...$(NC)"
	docker-compose down

## db-reset: Reset database (WARNING: Destroys all data)
db-reset:
	@echo "$(RED)Resetting database (this will destroy all data)...$(NC)"
	docker-compose down -v
	docker-compose up -d postgres
	@echo "$(YELLOW)Waiting for database to be ready...$(NC)"
	sleep 5
	docker-compose exec postgres psql -U ai_pm_user -d ai_pm_agent_dev -f /docker-entrypoint-initdb.d/001_initial_schema.sql
	@echo "$(GREEN)Database reset complete!$(NC)"

## db-migrate: Run database migrations
db-migrate:
	@echo "$(GREEN)Running database migrations...$(NC)"
	docker-compose exec postgres psql -U ai_pm_user -d ai_pm_agent_dev -f /docker-entrypoint-initdb.d/001_initial_schema.sql

## db-seed: Seed database with sample data
db-seed:
	@echo "$(GREEN)Seeding database with sample data...$(NC)"
	docker-compose exec postgres psql -U ai_pm_user -d ai_pm_agent_dev < database/seeds/sample_initiatives.sql

## db-shell: Open PostgreSQL shell
db-shell:
	@echo "$(GREEN)Opening database shell...$(NC)"
	docker-compose exec postgres psql -U ai_pm_user -d ai_pm_agent_dev

## docker-up: Start all services with Docker Compose
docker-up:
	@echo "$(GREEN)Starting all services...$(NC)"
	docker-compose up -d

## docker-down: Stop all services
docker-down:
	@echo "$(YELLOW)Stopping all services...$(NC)"
	docker-compose down

## docker-build: Build Docker image
docker-build:
	@echo "$(GREEN)Building Docker image...$(NC)"
	docker-compose build

## docker-logs: Show Docker logs
docker-logs:
	docker-compose logs -f

## setup: Complete development environment setup
setup: dev-install db-up
	@echo "$(GREEN)Setting up development environment...$(NC)"
	cp .env.example .env
	@echo "$(YELLOW)Please edit .env file with your API keys$(NC)"
	@echo "$(GREEN)Setup complete! Next steps:$(NC)"
	@echo "  1. Edit .env file with your credentials"
	@echo "  2. Run 'make db-migrate' to create database schema"
	@echo "  3. Run 'make db-seed' to load sample data"
	@echo "  4. Run 'make run' to start the agent"
