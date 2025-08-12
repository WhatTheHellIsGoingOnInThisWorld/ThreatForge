.PHONY: help install test run dev worker beat clean docker-build docker-run

help: ## Show this help message
	@echo "ThreatForge - Security Attack Simulation Platform"
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install Python dependencies
	pip install -r requirements.txt

test: ## Run project setup tests
	python test_setup.py

run: ## Start the FastAPI application
	python start.py

dev: ## Start development environment (API + Celery worker)
	@echo "Starting development environment..."
	@echo "Terminal 1: make run"
	@echo "Terminal 2: make worker"
	@echo "Terminal 3: make beat (optional)"

worker: ## Start Celery worker
	python scripts/start_celery.py

beat: ## Start Celery beat scheduler
	python scripts/start_celery.py beat

clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov

docker-build: ## Build Docker image
	docker build -t threatforge .

docker-run: ## Run with Docker Compose
	docker-compose up -d

docker-stop: ## Stop Docker Compose services
	docker-compose down

docker-logs: ## View Docker Compose logs
	docker-compose logs -f

db-migrate: ## Run database migrations
	alembic upgrade head

db-revision: ## Create new migration
	@read -p "Enter migration message: " message; \
	alembic revision --autogenerate -m "$$message"

db-downgrade: ## Downgrade database
	@read -p "Enter revision to downgrade to: " revision; \
	alembic downgrade $$revision

setup: install test ## Complete project setup
	@echo "Project setup complete!"
	@echo "Run 'make run' to start the application" 