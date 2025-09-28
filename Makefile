.PHONY: help setup test validate-all format lint clean install-hooks ci-local

# 기본 타겟
help:
	@echo "Available commands:"
	@echo "  make setup        - 개발 환경 설정"
	@echo "  make test         - 모든 테스트 실행"
	@echo "  make validate-all - 모든 Pine Script 검증"
	@echo "  make format       - 코드 포맷팅"
	@echo "  make lint         - 코드 린팅"
	@echo "  make clean        - 캐시 및 임시 파일 삭제"
	@echo "  make install-hooks - Pre-commit hooks 설치"
	@echo "  make ci-local     - 로컬에서 CI 파이프라인 실행"

# 개발 환경 설정
setup: requirements.txt
	python3 -m venv venv
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install -r requirements.txt
	make install-hooks
	@echo "✅ Setup complete! Activate venv with: source venv/bin/activate"

# 의존성 설치
install: requirements.txt
	pip install -r requirements.txt

# Pre-commit hooks 설치
install-hooks:
	pre-commit install
	@echo "✅ Pre-commit hooks installed"

# 모든 Pine Script 검증
validate-all:
	@echo "🔍 Validating all Pine Scripts..."
	@for file in $$(find strategies -name "*.pine"); do \
		echo "\n📊 Validating $$file"; \
		python tests/validator.py "$$file" || exit 1; \
	done
	@echo "\n✅ All validations passed!"

# RSI 전략 테스트
test-rsi:
	@echo "🧪 Testing RSI strategies..."
	@for file in $$(find strategies/momentum -name "*rsi*.pine"); do \
		echo "\n📊 Testing $$file"; \
		python tests/test_rsi_strategy.py "$$file" || exit 1; \
	done

# 모든 테스트 실행
test: validate-all test-rsi
	@echo "\n✅ All tests passed!"

# Python 코드 포맷팅
format:
	@echo "🎨 Formatting Python code..."
	black tests/
	isort tests/ --profile black
	@echo "✅ Formatting complete"

# 코드 린팅
lint:
	@echo "🔍 Running linters..."
	ruff check tests/ --fix
	mypy tests/ --ignore-missing-imports || true
	@echo "✅ Linting complete"

# 프로젝트 구조 확인
check-structure:
	@echo "📁 Checking project structure..."
	@python tests/check_structure.py
	@echo "✅ Structure check complete"

# 리포트 생성
report:
	@echo "📝 Generating validation report..."
	@mkdir -p reports
	@python tests/generate_report.py > reports/validation_report.md
	@echo "✅ Report generated: reports/validation_report.md"

# 캐시 및 임시 파일 삭제
clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf reports/
	@echo "✅ Cleanup complete"

# 로컬에서 CI 파이프라인 실행
ci-local: clean
	@echo "🚀 Running CI pipeline locally..."
	make lint
	make format
	make validate-all
	make test-rsi
	make check-structure
	make report
	@echo "\n✅ CI pipeline complete!"

# Pre-commit 실행
pre-commit:
	pre-commit run --all-files

# 의존성 업데이트 확인
check-deps:
	@echo "📦 Checking for dependency updates..."
	pip list --outdated

# ==================== Backtesting Commands ====================

# 백테스트 실행 (기본)
backtest:
	@echo "📈 Running RSI strategy backtest..."
	@python backtesting/run_backtest.py --strategy rsi --symbol AAPL --period 1y
	@echo "✅ Backtest complete! Check reports/backtest_results.html"

# 백테스트 실행 (커스텀 파라미터)
backtest-custom:
	@echo "📊 Running custom backtest..."
	@python backtesting/run_backtest.py \
		--strategy rsi \
		--symbol $(SYMBOL) \
		--period $(PERIOD) \
		--rsi-period $(RSI_PERIOD) \
		--oversold $(OVERSOLD) \
		--overbought $(OVERBOUGHT)

# 파라미터 최적화 실행
optimize:
	@echo "🔧 Running parameter optimization..."
	@python backtesting/optimize.py --strategy rsi --symbol AAPL
	@echo "✅ Optimization complete! Best parameters saved to reports/optimization_results.json"

# 멀티 심볼 백테스트
backtest-multi:
	@echo "🌐 Running multi-symbol backtest..."
	@python backtesting/run_backtest.py --strategy rsi --symbols "AAPL,GOOGL,MSFT,TSLA" --period 1y
	@echo "✅ Multi-symbol backtest complete!"

# 백테스트 리포트 보기
view-report:
	@echo "📊 Opening backtest report..."
	@python -m http.server 8000 -d reports &
	@open http://localhost:8000/backtest_results.html || xdg-open http://localhost:8000/backtest_results.html

# 백테스트 데이터 다운로드
download-data:
	@echo "📥 Downloading historical data..."
	@python backtesting/data/download.py --symbols "AAPL,GOOGL,MSFT,TSLA,SPY" --period 5y
	@echo "✅ Data download complete!"

# 백테스트 캐시 정리
clean-backtest:
	@echo "🧹 Cleaning backtest cache..."
	@rm -rf backtesting/data/cache/*
	@rm -rf reports/*.html
	@rm -rf reports/*.json
	@echo "✅ Backtest cache cleaned!"