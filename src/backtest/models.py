"""
Data models for backtesting system.

Defines BacktestResult, StrategyParameters, and other data structures
as required by TDD tests.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any


@dataclass
class BacktestResult:
    """Results from a backtest execution."""

    id: str
    strategy_id: str
    symbol: str
    initial_capital: Decimal
    final_capital: Decimal | None = None
    total_return: float | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    total_trades: int = 0
    win_rate: float = 0.0
    max_drawdown: float = 0.0
    sharpe_ratio: float | None = None
    profit_factor: float | None = None

    def __post_init__(self) -> None:
        """Calculate derived metrics after initialization."""
        if self.final_capital and self.initial_capital:
            self.total_return = float(
                (self.final_capital - self.initial_capital) / self.initial_capital
            )


@dataclass
class StrategyParameters:
    """Parameters for trading strategies."""

    name: str
    parameters: dict[str, Any]

    def get(self, key: str, default: Any = None) -> Any:
        """Get parameter value."""
        return self.parameters.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set parameter value."""
        self.parameters[key] = value


@dataclass
class OHLCVData:
    """OHLCV market data point."""

    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal

    def __post_init__(self) -> None:
        """Validate OHLCV relationships."""
        if not (self.low <= self.open <= self.high and self.low <= self.close <= self.high):
            raise ValueError("Invalid OHLCV relationships")


@dataclass
class TradeData:
    """Individual trade data."""

    entry_time: datetime
    exit_time: datetime | None
    entry_price: Decimal
    exit_price: Decimal | None
    quantity: Decimal
    pnl: Decimal | None = None

    def __post_init__(self) -> None:
        """Calculate PnL if exit data is available."""
        if self.exit_price and self.exit_time:
            self.pnl = (self.exit_price - self.entry_price) * self.quantity
