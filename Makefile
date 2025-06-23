.PHONY: build start stop down clean setup_laravel test_laravel test_worker test_frontend all

build:
	docker-compose build

start:
	docker-compose up -d

stop:
	docker-compose stop

down:
	docker-compose down

clean: down
	@echo "Removing Docker volumes and images..."
	docker volume rm $(docker volume ls -qf "name=$(PROJECT_NAME)_dbdata") || true
	docker rmi $(docker images -q "$(PROJECT_NAME)_*") || true

setup_laravel:
	@echo "Setting up Laravel application..."
	docker-compose exec app php artisan key:generate || true # Generate key if not exists
	docker-compose exec app php artisan migrate --force

test_laravel:
	@echo "Running Laravel backend tests..."
	docker-compose exec app php artisan test

test_worker:
	@echo "Running FastAPI worker tests..."
	docker-compose exec worker pytest /app/tests

test_frontend:
	@echo "Building Vue frontend for linting/tests (ESLint)..."
	docker-compose exec frontend npm install # Ensure dependencies are installed in container
	docker-compose exec frontend npm run lint -- --max-warnings 0 # Run lint, fail on warnings

# Default target for 'make'
all: build start setup_laravel
	@echo ""
	@echo -e "\033[0;32mProject setup complete!\033[0m"
	@echo ""
	@echo "Next steps:"
	@echo "1. If any changes to .env.example, copy it to .env: cp .env.example .env"
	@echo "2. Edit .env and fill in your API keys (OPENAI_API_KEY, HUGGINGFACE_API_TOKEN) and set APP_KEY for Laravel."
	@echo "3. If not already done by 'make all', manually setup Laravel:"
	@echo "   - Run 'docker-compose exec app php artisan key:generate'"
	@echo "   - Run 'docker-compose exec app php artisan migrate'"
	@echo "4. Access frontend: \033[1;33mhttp://localhost:5173\033[0m"
	@echo "5. Access FastAPI worker API docs (for health check or direct sync calls): \033[1;33mhttp://localhost:8001/docs\033[0m"
	@echo "   (The primary AI analysis is now handled asynchronously by the FastAPI consumer listening to Redis.)"
	@echo "6. To run queue worker for Laravel (if not using supervisor): docker-compose exec app php artisan queue:work redis --tries=3 --timeout=600"
	@echo ""
	@echo "Enjoy building InsightFlow, Eason!"
