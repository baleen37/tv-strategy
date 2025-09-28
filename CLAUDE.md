# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Early-stage TradingView strategy development and cryptocurrency backtesting framework. This project is currently in specification and foundational development phase, aimed at creating Pine Script v6 strategies with comprehensive testing and future trading bot extensibility.

## Current Development State

**Branch**: `001-tradingview-pine-script`  
**Status**: Foundational setup phase  
**Key Specification**: `specs/001-tradingview-pine-script/spec.md`

**What exists:**
- Project structure scaffolding (`src/`, `tests/`)
- Development tooling (Makefile, pyproject.toml, requirements.txt)
- Comprehensive specification document
- GitHub Actions CI/CD pipeline
- Pre-commit hooks configuration

**What's planned but not yet implemented:**
- Actual Pine Script strategies
- Python validation tools
- Backtesting framework
- Data fetching utilities

## Essential Commands

### Development Workflow
```bash
# Environment setup
make setup                    # Install dependencies and setup environment
source venv/bin/activate     # Activate virtual environment

# Code quality (when code exists)
make format                  # Format Python code with Black
make lint                    # Run Ruff linting and mypy
make test                    # Run all tests
make ci-local               # Run full CI pipeline locally

# Future strategy validation (not yet implemented)
make validate-all           # Validate all Pine Script files  
python tests/validator.py strategies/[file].pine    # Validate specific strategy
```

### Pre-commit Hooks
Automatically run on commit:
- Python code formatting (Black)
- Import sorting (isort) 
- Linting (Ruff)
- Future: Pine Script validation

## Project Architecture

### Directory Structure
```
tv-strategy/
├── specs/                           # Feature specifications
│   └── 001-tradingview-pine-script/  # Main feature spec
├── src/                             # Source code (minimal structure)
│   ├── strategies/                  # Pine Script strategies (empty)
│   ├── backtest/                    # Backtesting framework (empty)
│   └── data/                        # Data fetching utilities (empty)
├── tests/                           # Test framework (empty)
├── .github/workflows/               # CI/CD pipeline
├── Makefile                         # Development automation
├── pyproject.toml                   # Python project configuration
└── requirements.txt                 # Python dependencies
```

### Technology Stack
- **Strategy Language**: Pine Script v6 (TradingView)
- **Backend**: Python 3.9+ with pandas, ccxt for data
- **Testing**: pytest with comprehensive coverage requirements
- **Code Quality**: Black, isort, Ruff, mypy
- **Data Source**: Binance API (free tier)
- **CI/CD**: GitHub Actions with multi-Python testing

## Key Specifications

### Target Features (from spec)
- Cryptocurrency backtesting (BTC/USDT, ETH/USDT initially)
- Pine Script v6 strategy development
- Comprehensive validation and testing
- Performance metrics (returns, drawdown, Sharpe ratio)
- Future trading bot extensibility
- 95% test coverage requirement

### Trading Parameters
- **Position Types**: Long only initially (short positions planned)
- **Timeframes**: All standard (1M to 1W)
- **Commission/Slippage**: Exchange-specific presets
- **Validation**: Mandatory before execution

## Development Guidelines

### Code Quality Standards
- **Test Coverage**: Minimum 95% per constitution
- **Line Length**: 100 characters (Black configuration)
- **Type Hints**: Required for new Python code
- **Documentation**: Comprehensive inline documentation

### Strategy Development Process
1. Write comprehensive tests first (TDD approach)
2. Implement Pine Script strategy
3. Validate with Python validation tools
4. Run backtesting with multiple timeframes
5. Performance analysis and optimization

### Key Dependencies
```
ccxt>=4.0.0              # Cryptocurrency exchange APIs
pandas>=2.0.0            # Data analysis
pytest>=7.0.0            # Testing framework
ruff>=0.1.0              # Fast linting
black>=23.0.0            # Code formatting
```

## Common Tasks

### Adding New Strategy
1. Create Pine Script in appropriate strategy category
2. Add corresponding Python validation tests
3. Update Makefile validation targets
4. Run `make ci-local` to ensure quality standards

### Running Backtests (future)
```bash
# Basic backtest
make backtest

# Custom parameters  
make backtest-custom SYMBOL=BTC/USDT PERIOD=1y

# Multi-symbol testing
make backtest-multi
```

### Debugging Common Issues
- **Import errors**: Ensure virtual environment is activated
- **Lint failures**: Run `make format` before committing
- **Test failures**: Check 95% coverage requirement
- **API rate limits**: Binance free tier has limits

## Project Status Tracking

**Current Priority**: Implementing foundational Python validation and testing framework based on specification requirements.

**Next Steps**:
1. Implement Pine Script validator
2. Create basic RSI strategy as proof of concept
3. Build backtesting framework with Binance data integration
4. Establish comprehensive test suite

**Long-term Goal**: Extensible trading bot platform with robust strategy validation and risk management.

## Important Notes

- This project is in early development - many Makefile targets reference unimplemented features
- Always activate virtual environment before development
- Follow TDD approach - write tests before implementation
- Pine Script can only be executed on TradingView platform
- All backtesting should account for slippage and commission
- Future trading bot integration requires careful risk management