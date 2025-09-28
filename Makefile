.PHONY: help setup test validate-all format lint clean install-hooks ci-local

# 기본 타겟
help:
	@echo "📈 Cryptocurrency Backtesting System"
	@echo ""
	@echo "Development Commands:"
	@echo "  make setup           - 개발 환경 설정"
	@echo "  make test            - 모든 테스트 실행"
	@echo "  make validate-all    - 모든 Pine Script 검증"
	@echo "  make format          - 코드 포맷팅 (Python)"
	@echo "  make lint            - 코드 린팅"
	@echo "  make clean           - 캐시 및 임시 파일 삭제"
	@echo "  make install-hooks   - Pre-commit hooks 설치"
	@echo "  make ci-local        - 로컬에서 CI 파이프라인 실행"
	@echo ""
	@echo "Backtesting Commands:"
	@echo "  make backtest        - 기본 백테스트 실행"
	@echo "  make download-data   - 시장 데이터 다운로드"
	@echo "  make backtest-custom - 커스텀 파라미터 백테스트"
	@echo ""
	@echo "Strategy Commands:"
	@echo "  make test-rsi        - RSI 전략 테스트"
	@echo "  make validate-pine   - Pine Script 검증"

# 개발 환경 설정
setup:
	@echo "🚀 Setting up development environment..."
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
	@if [ -d "src/strategies" ]; then \
		for file in $$(find src/strategies -name "*.pine" 2>/dev/null); do \
			echo "\n📊 Validating $$file"; \
			python -m src.strategies.validator "$$file" || exit 1; \
		done; \
	else \
		echo "⚠️ No strategies directory found"; \
	fi
	@echo "\n✅ All validations passed!"

# RSI 전략 테스트
test-rsi:
	@echo "🧪 Testing RSI strategies..."
	@if [ -d "strategies/momentum" ]; then \
		for file in $$(find strategies/momentum -name "*rsi*.pine" 2>/dev/null); do \
			echo "\n📊 Testing $$file"; \
			python tests/test_rsi_strategy.py "$$file" || exit 1; \
		done; \
	else \
		echo "ℹ️ No RSI strategies found in strategies/momentum (directory may not exist)"; \
	fi

# 모든 테스트 실행
test:
	@echo "🧪 Running all tests..."
	python -m pytest tests/ -v --cov=src --cov-report=html --cov-report=term
	@echo "✅ All tests passed!"

# Pine Script 단일 검증
validate-pine:
	@if [ -z "$(FILE)" ]; then \
		echo "❌ Usage: make validate-pine FILE=path/to/file.pine"; \
		exit 1; \
	fi
	@echo "🔍 Validating $(FILE)..."
	@python -m src.strategies.validator "$(FILE)"
	@echo "✅ Validation complete!"

# Python 코드 포맷팅
format:
	@echo "🎨 Formatting Python code..."
	black src/ tests/
	isort src/ tests/ --profile black
	@echo "✅ Formatting complete"

# 코드 린팅
lint:
	@echo "🔍 Running linters..."
	ruff check src/ tests/ --fix
	mypy src/ tests/ --ignore-missing-imports || true
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
	@echo "📈 Running cryptocurrency backtest..."
	@python -m src.main backtest --symbol BTCUSDT
	@echo "✅ Backtest complete!"

# 백테스트 실행 (커스텀 파라미터)
backtest-custom:
	@echo "📊 Running custom backtest..."
	@if [ -z "$(SYMBOL)" ]; then \
		echo "❌ Usage: make backtest-custom SYMBOL=BTCUSDT [INITIAL_CAPITAL=10000]"; \
		exit 1; \
	fi
	@python -m src.main backtest \
		--symbol $(SYMBOL) \
		--initial-capital $(or $(INITIAL_CAPITAL),10000) \
		--commission-rate $(or $(COMMISSION_RATE),0.001)

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
	@python -m src.main download \
		--symbol $(or $(SYMBOL),BTCUSDT) \
		--timeframe $(or $(TIMEFRAME),1d) \
		--limit $(or $(LIMIT),100)
	@echo "✅ Data download complete!"

# 백테스트 데이터 정리
clean-data:
	@echo "🧹 Cleaning market data..."
	@rm -rf data/*.parquet
	@echo "✅ Market data cleaned!"

# 사용 예시 출력
examples:
	@echo "📋 Usage Examples:"
	@echo ""
	@echo "# 기본 백테스트"
	@echo "make backtest"
	@echo ""
	@echo "# 커스텀 백테스트"
	@echo "make backtest-custom SYMBOL=ETHUSDT INITIAL_CAPITAL=50000"
	@echo ""
	@echo "# 데이터 다운로드"
	@echo "make download-data SYMBOL=BTCUSDT TIMEFRAME=1h LIMIT=500"
	@echo ""
	@echo "# Pine Script 검증"
	@echo "make validate-pine FILE=src/strategies/rsi_basic.pine"
