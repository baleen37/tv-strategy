# Tasks: Cryptocurrency Backtesting System

**Input**: Design documents from `/specs/001-tradingview-pine-script/`
**Prerequisites**: plan.md (required), research.md, data-model.md, quickstart.md

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → Tech stack: Python 3.11, ccxt, pandas, pytest
   → Structure: src/ with data/backtest/strategies modules
2. Load design documents:
   → data-model.md: 8 entities (OHLCVData, Trade, BacktestResult, etc.)
   → quickstart.md: CLI scenarios, data download, test execution
   → No contracts/ API (CLI-only per plan)
3. Generate tasks by category:
   → Setup: project structure, dependencies, pre-commit
   → Tests: TDD approach with failing tests first
   → Core: data collection, backtesting engine, Pine Script
   → Integration: end-to-end workflows
   → Polish: performance, 95% coverage validation
4. Apply task rules:
   → Different modules = [P] for parallel
   → TDD: tests before implementation
   → 95% coverage requirement (Constitution)
5. Number tasks sequentially (T001-T018)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Phase 3.1: Setup & Structure
- [x] T001 Update pyproject.toml with Black/Ruff/mypy configuration for Constitution compliance
- [x] T002 Configure pre-commit hooks in .pre-commit-config.yaml with ruff, black, isort, mypy
- [x] T003 [P] Create .gitignore for Python project (venv/, __pycache__, *.pyc, data/*.parquet)

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [x] T004 [P] Data collection test in tests/test_data.py for CCXT client download/validation
- [x] T005 [P] Backtest engine test in tests/test_backtest.py for RSI strategy execution
- [x] T006 [P] Pine Script validation test in tests/test_pine.py for template.pine syntax checking
- [x] T007 [P] Integration test in tests/test_integration.py for complete backtest workflow

## Phase 3.3: Core Implementation (ONLY after tests are failing)
- [ ] T008 [P] CCXT client in src/data/ccxt_client.py with Binance API integration and error handling
- [ ] T009 [P] Data storage in src/data/storage.py for Parquet read/write operations
- [ ] T010 [P] Backtest engine in src/backtest/engine.py with portfolio management and trade execution
- [ ] T011 [P] Performance metrics in src/backtest/metrics.py with Sharpe, drawdown, win rate calculations
- [ ] T012 [P] Pine Script template in src/strategies/template.pine with v6 syntax and RSI example
- [ ] T013 [P] Basic RSI strategy in src/strategies/rsi_basic.pine implementing buy/sell signals
- [ ] T014 Main CLI entry point in src/main.py with argparse for backtest commands

## Phase 3.4: Integration & Workflows
- [ ] T015 Pine Script validator in tests/test_pine.py with v6 syntax and strategy structure checks
- [ ] T016 End-to-end workflow connecting data download → backtest → results output
- [ ] T017 Error handling and logging for CCXT API failures and data quality issues

## Phase 3.5: Polish & Validation
- [ ] T018 [P] Verify 95% test coverage with pytest --cov=src --cov-fail-under=95 (Constitution requirement)

## Dependencies
- Setup (T001-T003) before tests (T004-T007)
- Tests (T004-T007) before implementation (T008-T014)
- T008-T009 (data layer) before T010-T011 (backtest engine)
- T012-T013 (Pine Script) independent of other core tasks
- T014 (CLI) depends on T008-T011 completion
- Implementation before integration (T015-T017)
- All before coverage validation (T018)

## Parallel Example
```
# Launch T004-T007 together (TDD phase):
Task: "Data collection test in tests/test_data.py for CCXT client download/validation"
Task: "Backtest engine test in tests/test_backtest.py for RSI strategy execution"
Task: "Pine Script validation test in tests/test_pine.py for template.pine syntax checking"
Task: "Integration test in tests/test_integration.py for complete backtest workflow"

# Launch T008-T013 together (core implementation):
Task: "CCXT client in src/data/ccxt_client.py with Binance API integration"
Task: "Data storage in src/data/storage.py for Parquet read/write operations"
Task: "Backtest engine in src/backtest/engine.py with portfolio management"
Task: "Performance metrics in src/backtest/metrics.py with Sharpe/drawdown calculations"
Task: "Pine Script template in src/strategies/template.pine with v6 syntax"
Task: "Basic RSI strategy in src/strategies/rsi_basic.pine implementing signals"
```

## Constitution Compliance Notes
- **95% Test Coverage**: T018 validates with --cov-fail-under=95
- **Code Quality**: T001-T002 enforce Black, Ruff, mypy via pre-commit
- **Architecture Integrity**: Clear separation: data/ → backtest/ → strategies/
- **YAGNI Principle**: Only essential features, no web API, minimal dependencies
- **TDD Approach**: All tests (T004-T007) before implementation (T008-T014)

## Quickstart Validation Scenarios
Based on quickstart.md requirements:
1. T008: `python -m src.data.ccxt_client download BTCUSDT 1d 100`
2. T014: `python -m src.main backtest --symbol BTCUSDT`
3. T015: `python -m tests.test_pine src/strategies/rsi_basic.pine`
4. T018: `pytest --cov=src --cov-report=term-missing`

## File Structure After Completion
```
src/
├── data/
│   ├── ccxt_client.py    # T008
│   └── storage.py        # T009
├── backtest/
│   ├── engine.py         # T010
│   └── metrics.py        # T011
├── strategies/
│   ├── template.pine     # T012
│   └── rsi_basic.pine    # T013
└── main.py               # T014

tests/
├── test_data.py          # T004
├── test_backtest.py      # T005
├── test_pine.py          # T006
└── test_integration.py   # T007
```

## Notes
- **CLI-only**: No web API implementation (per plan.md decision)
- **CCXT Priority**: Research.md emphasizes CCXT for reliable data collection
- **Minimal Scope**: 2 symbols (BTC/USDT, ETH/USDT), basic RSI strategy only
- **Constitution**: 95% coverage, strict linting, TDD approach mandatory
- **Error Recovery**: 5-level CCXT error handling (per research.md)

## Validation Checklist
*GATE: Checked before task execution*

- [x] All entities have model representations in core tasks
- [x] All tests come before implementation (T004-T007 → T008-T014)
- [x] Parallel tasks truly independent (different modules/files)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] Constitution compliance validated (T001-T002, T018)
- [x] Quickstart scenarios covered in tasks
