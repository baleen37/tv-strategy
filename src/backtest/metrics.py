"""
Performance metrics calculation for backtesting results.

Implements PerformanceMetrics, RiskMetrics, and TradeAnalyzer classes
as required by TDD tests.
"""

import logging
import math
from datetime import timedelta
from decimal import Decimal
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """Calculate trading performance metrics."""

    def __init__(self, initial_capital: Decimal):
        """Initialize metrics calculator.

        Args:
            initial_capital: Starting portfolio capital
        """
        self.initial_capital = initial_capital

    def calculate_total_return(self, final_value: Decimal) -> Decimal:
        """Calculate total return percentage.

        Args:
            final_value: Final portfolio value

        Returns:
            Total return as decimal (e.g., 0.125 for 12.5%)
        """
        return (final_value - self.initial_capital) / self.initial_capital

    def calculate_win_rate(self, trades: list[Any]) -> float:
        """Calculate win rate from trades.

        Args:
            trades: List of Trade objects

        Returns:
            Win rate as decimal (0.0 to 1.0)
        """
        if not trades:
            return 0.0

        winning_trades = sum(1 for trade in trades if trade.pnl and trade.pnl > 0)
        return winning_trades / len(trades)

    def calculate_sharpe_ratio(
        self, returns: pd.Series, risk_free_rate: float = 0.02, periods_per_year: int = 252
    ) -> float:
        """Calculate Sharpe ratio.

        Args:
            returns: Series of period returns
            risk_free_rate: Annual risk-free rate
            periods_per_year: Number of periods per year

        Returns:
            Sharpe ratio
        """
        if returns.empty or returns.std() == 0:
            return 0.0

        # Convert annual risk-free rate to period rate
        period_risk_free = risk_free_rate / periods_per_year

        excess_returns = returns - period_risk_free
        return float(excess_returns.mean() / returns.std() * math.sqrt(periods_per_year))

    def calculate_max_drawdown(self, portfolio_values: pd.Series) -> float:
        """Calculate maximum drawdown.

        Args:
            portfolio_values: Series of portfolio values over time

        Returns:
            Maximum drawdown as negative decimal
        """
        if portfolio_values.empty:
            return 0.0

        # Calculate running maximum
        running_max = portfolio_values.expanding().max()

        # Calculate drawdown
        drawdown = (portfolio_values - running_max) / running_max

        return float(drawdown.min())

    def calculate_profit_factor(self, trades: list[Any]) -> float:
        """Calculate profit factor.

        Args:
            trades: List of Trade objects

        Returns:
            Profit factor (gross profit / gross loss)
        """
        if not trades:
            return 0.0

        gross_profit = sum(float(trade.pnl) for trade in trades if trade.pnl and trade.pnl > 0)

        gross_loss = abs(sum(float(trade.pnl) for trade in trades if trade.pnl and trade.pnl < 0))

        if gross_loss == 0:
            return float("inf") if gross_profit > 0 else 0.0

        return gross_profit / gross_loss

    def calculate_sortino_ratio(
        self, returns: pd.Series, risk_free_rate: float = 0.02, periods_per_year: int = 252
    ) -> float:
        """Calculate Sortino ratio (downside deviation only).

        Args:
            returns: Series of period returns
            risk_free_rate: Annual risk-free rate
            periods_per_year: Number of periods per year

        Returns:
            Sortino ratio
        """
        if returns.empty:
            return 0.0

        period_risk_free = risk_free_rate / periods_per_year
        excess_returns = returns - period_risk_free

        # Calculate downside deviation
        negative_returns = returns[returns < period_risk_free]
        if negative_returns.empty:
            return float("inf") if excess_returns.mean() > 0 else 0.0

        downside_deviation = negative_returns.std()
        if downside_deviation == 0:
            return float("inf") if excess_returns.mean() > 0 else 0.0

        return float(excess_returns.mean() / downside_deviation * math.sqrt(periods_per_year))


class RiskMetrics:
    """Calculate risk-related metrics."""

    def __init__(self) -> None:
        """Initialize risk metrics calculator."""
        pass

    def calculate_var(self, returns: pd.Series, confidence_level: float = 0.05) -> float:
        """Calculate Value at Risk (VaR).

        Args:
            returns: Series of returns
            confidence_level: Confidence level (e.g., 0.05 for 95% VaR)

        Returns:
            VaR value
        """
        if returns.empty:
            return 0.0

        return float(returns.quantile(confidence_level))

    def calculate_cvar(self, returns: pd.Series, confidence_level: float = 0.05) -> float:
        """Calculate Conditional Value at Risk (CVaR).

        Args:
            returns: Series of returns
            confidence_level: Confidence level

        Returns:
            CVaR value
        """
        if returns.empty:
            return 0.0

        var = self.calculate_var(returns, confidence_level)
        return float(returns[returns <= var].mean())

    def calculate_volatility(self, returns: pd.Series, periods_per_year: int = 252) -> float:
        """Calculate annualized volatility.

        Args:
            returns: Series of returns
            periods_per_year: Number of periods per year

        Returns:
            Annualized volatility
        """
        if returns.empty:
            return 0.0

        return float(returns.std() * math.sqrt(periods_per_year))


class TradeAnalyzer:
    """Analyze individual trades and patterns."""

    def __init__(self) -> None:
        """Initialize trade analyzer."""
        pass

    def analyze_trades(self, trades: list[Any]) -> dict[str, Any]:
        """Analyze trade statistics.

        Args:
            trades: List of Trade objects

        Returns:
            Dictionary with trade analysis
        """
        if not trades:
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
                "avg_win": 0.0,
                "avg_loss": 0.0,
                "best_trade": None,
                "worst_trade": None,
                "avg_duration": timedelta(0),
            }

        winning_trades = [t for t in trades if t.pnl and t.pnl > 0]
        losing_trades = [t for t in trades if t.pnl and t.pnl < 0]

        avg_win = (
            sum(float(t.pnl) for t in winning_trades) / len(winning_trades)
            if winning_trades
            else 0.0
        )

        avg_loss = (
            sum(float(t.pnl) for t in losing_trades) / len(losing_trades) if losing_trades else 0.0
        )

        return {
            "total_trades": len(trades),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": len(winning_trades) / len(trades),
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "best_trade": self.find_best_trade(trades),
            "worst_trade": self.find_worst_trade(trades),
            "avg_duration": self.calculate_average_duration(trades),
        }

    def find_best_trade(self, trades: list[Any]) -> Any | None:
        """Find the most profitable trade.

        Args:
            trades: List of Trade objects

        Returns:
            Best performing trade
        """
        if not trades:
            return None

        profitable_trades = [t for t in trades if t.pnl and t.pnl > 0]
        if not profitable_trades:
            return None

        return max(profitable_trades, key=lambda t: t.pnl)

    def find_worst_trade(self, trades: list[Any]) -> Any | None:
        """Find the least profitable trade.

        Args:
            trades: List of Trade objects

        Returns:
            Worst performing trade
        """
        if not trades:
            return None

        return min(trades, key=lambda t: t.pnl if t.pnl else Decimal(0))

    def calculate_average_duration(self, trades: list[Any]) -> timedelta:
        """Calculate average trade duration.

        Args:
            trades: List of Trade objects

        Returns:
            Average trade duration
        """
        durations = []

        for trade in trades:
            if hasattr(trade, "duration") and trade.duration:
                durations.append(trade.duration)
            elif (
                hasattr(trade, "entry_time")
                and hasattr(trade, "exit_time")
                and trade.entry_time
                and trade.exit_time
            ):
                durations.append(trade.exit_time - trade.entry_time)

        if not durations:
            return timedelta(0)

        total_seconds = sum(d.total_seconds() for d in durations)
        avg_seconds = total_seconds / len(durations)

        return timedelta(seconds=avg_seconds)

    def analyze_drawdown_periods(self, equity_curve: pd.Series) -> dict[str, Any]:
        """Analyze drawdown periods.

        Args:
            equity_curve: Series of portfolio values

        Returns:
            Drawdown analysis
        """
        if equity_curve.empty:
            return {
                "max_drawdown": 0.0,
                "avg_drawdown": 0.0,
                "drawdown_periods": 0,
                "max_drawdown_duration": timedelta(0),
            }

        # Calculate running maximum and drawdown
        running_max = equity_curve.expanding().max()
        drawdown = (equity_curve - running_max) / running_max

        # Find drawdown periods
        in_drawdown = drawdown < 0
        drawdown_periods = []

        start_idx = None
        for i, is_dd in enumerate(in_drawdown):
            if is_dd and start_idx is None:
                start_idx = i
            elif not is_dd and start_idx is not None:
                drawdown_periods.append((start_idx, i - 1))
                start_idx = None

        # Handle case where we end in drawdown
        if start_idx is not None:
            drawdown_periods.append((start_idx, len(in_drawdown) - 1))

        max_dd_duration = timedelta(0)
        if drawdown_periods and hasattr(equity_curve.index, "to_pydatetime"):
            for start, end in drawdown_periods:
                duration = equity_curve.index[end] - equity_curve.index[start]
                if duration > max_dd_duration:
                    max_dd_duration = duration

        return {
            "max_drawdown": float(drawdown.min()),
            "avg_drawdown": float(drawdown[drawdown < 0].mean()) if any(drawdown < 0) else 0.0,
            "drawdown_periods": len(drawdown_periods),
            "max_drawdown_duration": max_dd_duration,
        }
