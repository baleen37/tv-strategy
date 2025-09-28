# TV Strategy - Cryptocurrency Backtesting System

.DEFAULT_GOAL := help
.PHONY: help install check test clean run data ci

# Variables
PYTHON ?= python3
SRC := src tests
SYMBOL ?= BTCUSDT

# Help
help: ## Show help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-8s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Install dependencies
install: ## Install dependencies
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m pip install pre-commit
	pre-commit install

# Code quality checks (CI-friendly)
check: ## Check code quality (format + lint + types)
	black --check $(SRC)
	isort --check-only $(SRC) --profile black
	ruff check $(SRC)
	mypy $(SRC) --ignore-missing-imports || echo "⚠️ Type checking found issues (non-blocking)"

# Run tests
test: ## Run tests with coverage
	$(PYTHON) -m pytest tests/ -v --cov=src --cov-report=term --cov-fail-under=95

# Clean cache files
clean: ## Clean cache files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .mypy_cache .ruff_cache .pytest_cache htmlcov .coverage

# Run backtest
run: ## Run backtest [SYMBOL=BTCUSDT]
	$(PYTHON) -m src.main backtest --symbol $(SYMBOL)

# Download data
data: ## Download data [SYMBOL=BTCUSDT]
	$(PYTHON) -m src.main download --symbol $(SYMBOL)

# CI pipeline
ci: check test ## Run CI pipeline (check + test)
