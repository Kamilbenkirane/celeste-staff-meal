.PHONY: help sync lint lint-fix format typecheck test integration-test security ci clean generate-mock-data deploy check-env

# Default target
help:
	@echo "Available commands:"
	@echo "  make sync       - Update and sync all dependencies"
	@echo "  make lint       - Run Ruff linting"
	@echo "  make format     - Apply Ruff formatting"
	@echo "  make typecheck  - Run mypy type checking"
	@echo "  make test       - Run all tests with coverage"
	@echo "  make integration-test - Run integration tests (requires API keys)"
	@echo "  make security   - Run Bandit security scan"
	@echo "  make ci       - Run full CI/CD pipeline"
	@echo "  make clean      - Clean cache directories"
	@echo "  make generate-mock-data - Generate mock validation records (NUM_RECORDS=100 DAYS=30)"
	@echo "  make deploy     - Deploy to Streamlit Cloud"

# Complete dependency sync - update lock, sync everything
sync:
	@echo "🔄 Updating dependencies..."
	@uv sync --upgrade
	@echo "✅ All dependencies synced and updated"

# Linting
lint:
	uv run ruff check src/staff_meal tests/

# Linting with auto-fix
lint-fix:
	uv run ruff check --fix src/staff_meal tests/

# Formatting
format:
	uv run ruff format src/staff_meal tests/

# Type checking (fail fast on any error)
typecheck:
	@uv run mypy -p staff_meal
	@if [ -n "$$(find tests -name '*.py' 2>/dev/null)" ]; then uv run mypy tests/; fi

# Testing
test:
	@if [ -n "$$(find tests -name 'test_*.py' -o -name '*_test.py' 2>/dev/null)" ]; then \
		uv run pytest tests/unit_tests --cov=staff_meal --cov-report=term-missing --cov-fail-under=80 -v; \
	else \
		echo "⚠️  No tests found, skipping test run"; \
	fi

# Integration testing (requires API keys)
integration-test:
	uv run pytest tests/integration_tests/ -m integration -v --dist=worksteal -n auto

# Security scanning (config reads from pyproject.toml)
security:
	uv run bandit -c pyproject.toml -r src/ -f screen

# Full CI/CD pipeline - what GitHub Actions will run
ci:
	@echo "🔍 Running Full CI/CD Pipeline..."
	@echo "================================="
	@echo "1️⃣  Ruff Linting (with auto-fix)..."
	@$(MAKE) lint-fix || (echo "❌ Linting failed" && exit 1)
	@echo "✅ Linting passed"
	@echo ""
	@echo "2️⃣  Ruff Formatting..."
	@$(MAKE) format || (echo "❌ Formatting failed" && exit 1)
	@echo "✅ Formatting applied"
	@echo ""
	@echo "3️⃣  MyPy Type Checking (parallel)..."
	@$(MAKE) typecheck || (echo "❌ Type checking failed" && exit 1)
	@echo "✅ Type checking passed"
	@echo ""
	@echo "4️⃣  Bandit Security Scan..."
	@$(MAKE) security || (echo "❌ Security scan failed" && exit 1)
	@echo "✅ Security scan passed"
	@echo ""
	@echo "5️⃣  Running Tests with Coverage..."
	@$(MAKE) test || (echo "❌ Tests failed" && exit 1)
	@echo ""
	@echo "================================="
	@echo "🎉 All CI/CD checks passed! Ready to commit."

# Clean cache directories and artifacts
clean:
	@echo "🧹 Cleaning cache directories and artifacts..."
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov/
	rm -rf __pycache__ build/ dist/ *.egg-info .eggs/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	@echo "✅ Clean complete"

# Delete mock data from database
clean-mock-data:
	@echo "🗑️  Deleting mock validation records..."
	@PYTHONPATH=src:. uv run python scripts/delete_mock_data.py
	@echo "✅ Mock data deletion complete"

# Generate mock data for testing dashboard
generate-mock-data:
	@echo "📊 Generating mock validation records..."
	@NUM_RECORDS=$${NUM_RECORDS:-100}; \
	DAYS=$${DAYS:-90}; \
	PYTHONPATH=src:. uv run python scripts/generate_mock_data.py $$NUM_RECORDS $$DAYS
	@echo "✅ Mock data generation complete"

# Reset mock data (delete and regenerate)
reset-mock-data: clean-mock-data generate-mock-data
	@echo "🔄 Mock data reset complete"

# Deployment to Streamlit Cloud
deploy: check-env
	@echo "🚀 Deploying to Streamlit Cloud..."
	@echo ""
	@echo "📋 Steps:"
	@echo "1. Go to https://share.streamlit.io"
	@echo "2. Sign in with GitHub"
	@echo "3. Click 'New app'"
	@echo "4. Repository: Kamilbenkirane/celeste-staff-meal"
	@echo "5. Main file: app.py"
	@echo "6. Set environment variables in app settings"
	@echo ""
	@echo "✅ Repository is ready for deployment!"

check-env:
	@echo "🔍 Checking environment variables..."
	@test -n "$$SUPABASE_URL" || (echo "⚠️  SUPABASE_URL not set (will need to set in Streamlit Cloud)" && exit 0)
	@test -n "$$SUPABASE_KEY" || (echo "⚠️  SUPABASE_KEY not set (will need to set in Streamlit Cloud)" && exit 0)
	@echo "✅ Local environment variables found"
