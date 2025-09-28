# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Complete cryptocurrency backtesting system** with TradingView Pine Script v6 strategies, Python backend, and comprehensive testing framework. The system is fully functional with data fetching, strategy validation, backtesting execution, and performance analysis capabilities.

## Current Development State

**Branch**: `main`  
**Status**: Production-ready implementation  
**Key Specification**: `specs/001-tradingview-pine-script/spec.md`

**Implemented features:**
- Complete Python backtesting framework (`src/backtest/`)
- CCXT-based cryptocurrency data fetching (`src/data/`)
- Pine Script strategy validation tools (`src/strategies/`)
- RSI momentum strategy implementation
- Comprehensive CLI interface (`src/main.py`)
- 95%+ test coverage with pytest
- Risk management and portfolio tracking
- Performance metrics (returns, drawdown, Sharpe ratio)

## Essential Commands

### Development Workflow
```bash
# Environment setup
make setup                    # Install dependencies and setup environment
source venv/bin/activate     # Activate virtual environment

# Code quality
make format                  # Format Python code with Black
make lint                    # Run Ruff linting and mypy
make test                    # Run all tests with coverage
make ci-local               # Run full CI pipeline locally

# Strategy validation
make validate-all           # Validate all Pine Script files
python -m src.strategies.validator strategies/[file].pine    # Validate specific strategy

# Backtesting commands
python -m src.main backtest --symbol BTCUSDT    # Run basic backtest
python -m src.main download --symbol BTCUSDT --timeframe 1d --limit 100    # Download data
python -m src.main validate --file src/strategies/rsi_basic.pine    # Validate Pine Script
```

### Pre-commit Hooks
Automatically run on commit:
- Python code formatting (Black)
- Import sorting (isort) 
- Linting (Ruff)
- Type checking (mypy)
- Pine Script validation

## Project Architecture

### Core Architecture
This is a **three-layer system**:
1. **Data Layer** (`src/data/`): CCXT-based cryptocurrency data fetching and Parquet storage
2. **Strategy Layer** (`src/strategies/`): Pine Script strategies with Python validation tools
3. **Execution Layer** (`src/backtest/`): Portfolio management, trade execution, and performance analysis

### Directory Structure
```
tv-strategy/
├── specs/                           # Feature specifications and requirements
├── src/                             # Main source code
│   ├── backtest/                    # Backtesting engine
│   │   ├── engine.py                #   Portfolio and trade execution
│   │   ├── metrics.py               #   Performance calculations
│   │   └── models.py                #   Data models and results
│   ├── data/                        # Data management
│   │   ├── ccxt_client.py           #   Cryptocurrency data fetching
│   │   └── storage.py               #   Parquet file storage
│   ├── strategies/                  # Trading strategies
│   │   ├── rsi_basic.pine           #   RSI momentum strategy
│   │   ├── template.pine            #   Strategy boilerplate
│   │   ├── validator.py             #   Pine Script validation
│   │   ├── parser.py                #   Strategy parsing
│   │   └── analyzer.py              #   Strategy analysis
│   └── main.py                      # CLI entry point
├── tests/                           # Comprehensive test suite
├── data/                           # Market data storage (Parquet files)
└── htmlcov/                        # Test coverage reports
```

### Technology Stack
- **Strategy Language**: Pine Script v6 (TradingView)
- **Backend**: Python 3.11+ with pandas, ccxt, decimal precision
- **Testing**: pytest with 95%+ coverage, TDD methodology
- **Code Quality**: Black, isort, Ruff, mypy with strict typing
- **Data Storage**: Parquet files for efficient market data storage
- **Data Source**: Binance API (free tier) via CCXT library
- **CLI**: argparse-based command interface

## Key Architecture Components

### Backtesting Engine (`src/backtest/`)
- **Portfolio Management**: Position sizing, risk management, capital allocation
- **Trade Execution**: Entry/exit logic, commission handling, slippage simulation
- **Performance Analysis**: Returns, drawdown, Sharpe ratio, win/loss tracking
- **Risk Controls**: Stop-loss, take-profit, maximum drawdown limits

### Data Management (`src/data/`)
- **DataDownloader**: CCXT-based cryptocurrency data fetching from Binance
- **ParquetStorage**: Efficient storage and retrieval of OHLCV market data
- **Symbols Supported**: BTC/USDT, ETH/USDT (expandable to any CCXT-supported pairs)
- **Timeframes**: 1m, 5m, 15m, 1h, 4h, 1d, 1w

### Strategy Framework (`src/strategies/`)
- **Pine Script Validation**: Syntax checking, version verification, strategy structure validation
- **RSI Strategy**: Complete implementation with configurable parameters
- **Template System**: Boilerplate for new strategy development
- **Analysis Tools**: Strategy performance analysis and optimization

## Development Guidelines

### Code Quality Standards
- **Test Coverage**: Minimum 95% required (automatically enforced)
- **Line Length**: 100 characters (Black configuration)
- **Type Hints**: Required for all Python code (mypy enforced)
- **Documentation**: Comprehensive docstrings following Google style
- **Decimal Precision**: All financial calculations use `decimal.Decimal` for accuracy

### Strategy Development Workflow
1. **Pine Script Development**: Create strategy in `src/strategies/` following template
2. **Validation**: Run `python -m src.strategies.validator [file].pine` 
3. **Python Testing**: Add comprehensive tests for strategy logic
4. **Backtesting**: Test with `python -m src.main backtest --symbol [SYMBOL]`
5. **Performance Analysis**: Review metrics and optimize parameters

### Trading Bot Extensibility Design
The system is designed for future trading bot integration:
- **Modular Strategy Interface**: Strategies implement common interface for live trading
- **Risk Management**: Portfolio-level controls ready for live execution
- **Data Pipeline**: Real-time data integration prepared through CCXT
- **Trade Execution**: Engine supports both backtesting and live trading modes

## Common Development Tasks

### Running Tests
```bash
# Full test suite with coverage
make test

# Single test file
python -m pytest tests/test_backtest.py -v

# Coverage report
python -m pytest --cov=src --cov-report=html
```

### Data Management
```bash
# Download fresh market data
python -m src.main download --symbol BTCUSDT --timeframe 1d --limit 500

# List available data files
ls data/

# View data file info
python -c "import pandas as pd; print(pd.read_parquet('data/BTCUSDT_1d_100.parquet').info())"
```

### Strategy Backtesting
```bash
# Quick backtest with defaults
python -m src.main backtest --symbol BTCUSDT

# Custom parameters
python -m src.main backtest --symbol ETHUSDT --initial-capital 50000 --commission-rate 0.002

# Advanced backtest through Makefile
make backtest-custom SYMBOL=BTCUSDT PERIOD=2y
```

### Debugging Common Issues
- **Import errors**: Ensure virtual environment is activated with `source venv/bin/activate`
- **Lint failures**: Run `make format` then `make lint` before committing
- **Test failures**: Check that test coverage remains above 95%
- **API rate limits**: Binance free tier has request limits - use cached data when possible
- **Data file not found**: Download data first with `python -m src.main download`
- **Decimal precision errors**: All financial calculations must use `decimal.Decimal`

### Key Implementation Details

**Financial Precision**: The system uses `decimal.Decimal` throughout for all financial calculations to avoid floating-point precision issues common in trading systems.

**Data Storage**: Market data is stored in Parquet format for efficient compression and fast loading. Files are named as `{SYMBOL}_{TIMEFRAME}_{LIMIT}.parquet`.

**Strategy Interface**: Pine Script strategies are validated by Python tools but executed conceptually - the backtesting engine implements the strategy logic in Python for historical testing.

**Risk Management**: Built-in portfolio-level risk controls including stop-loss, take-profit, and maximum drawdown protection suitable for live trading extension.

**Testing Philosophy**: Comprehensive TDD approach with unit tests for individual components, integration tests for workflow validation, and end-to-end tests for complete system verification.

## Important Notes

- **Production Ready**: System is fully functional with real market data and comprehensive testing
- **Virtual Environment Required**: Always activate venv before development work
- **Pine Script Execution**: Strategies validated locally but executed on TradingView platform
- **Commission Handling**: All backtests include realistic commission and slippage calculations
- **Trading Bot Ready**: Architecture designed for seamless extension to live trading systems