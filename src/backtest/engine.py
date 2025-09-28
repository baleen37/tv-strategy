"""
Backtest engine with portfolio management and strategy execution.

Implements Portfolio, BacktestEngine, RSIStrategy, and Trade classes
as required by TDD tests.
"""

import logging
import uuid
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from src.backtest.models import BacktestResult

logger = logging.getLogger(__name__)


class Trade:
    """Represents a single trade."""

    def __init__(
        self,
        id: str | None = None,
        symbol: str = "",
        side: str = "long",
        entry_price: Decimal | None = None,
        exit_price: Decimal | None = None,
        quantity: Decimal | None = None,
        entry_time: datetime | None = None,
        exit_time: datetime | None = None,
        stop_loss: Decimal | None = None,
        take_profit: Decimal | None = None,
        status: str = "open",
        pnl: Decimal | None = None,
        pnl_percent: float | None = None,
        entry_commission: Decimal | None = None,
        exit_commission: Decimal | None = None,
        exit_reason: str | None = None,
    ):
        """Initialize trade.

        Args:
            id: Unique trade identifier
            symbol: Trading pair symbol
            side: Trade side (long/short)
            entry_price: Entry price
            exit_price: Exit price
            quantity: Position size
            entry_time: Entry timestamp
            exit_time: Exit timestamp
            stop_loss: Stop loss price
            take_profit: Take profit price
            status: Trade status (open/closed)
            pnl: Profit/loss amount
            pnl_percent: Profit/loss percentage
            entry_commission: Entry commission
            exit_commission: Exit commission
            exit_reason: Reason for exit (signal/stop_loss/take_profit)
        """
        self.id = id or str(uuid.uuid4())
        self.symbol = symbol
        self.side = side
        self.entry_price = entry_price
        self.exit_price = exit_price
        self.quantity = quantity
        self.entry_time = entry_time
        self.exit_time = exit_time
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.status = status
        self.pnl = pnl
        self.pnl_percent = pnl_percent
        self.entry_commission = entry_commission or Decimal("0.0")
        self.exit_commission = exit_commission or Decimal("0.0")
        self.exit_reason = exit_reason

        # Calculate duration if both times are available
        self.duration = None
        if self.entry_time and self.exit_time:
            self.duration = self.exit_time - self.entry_time


class Signal:
    """Represents a trading signal."""

    def __init__(
        self, timestamp: datetime, signal_type: str, strength: float = 0.0, confidence: float = 0.5
    ):
        """Initialize signal.

        Args:
            timestamp: Signal timestamp
            signal_type: Signal type (buy/sell/hold)
            strength: Signal strength (-1.0 to 1.0)
            confidence: Signal confidence (0.0 to 1.0)
        """
        self.timestamp = timestamp
        self.signal_type = signal_type
        self.strength = strength
        self.confidence = confidence


class Portfolio:
    """Portfolio management with position tracking."""

    def __init__(self, initial_capital: Decimal, commission_rate: Decimal = Decimal("0.001")):
        """Initialize portfolio.

        Args:
            initial_capital: Starting capital
            commission_rate: Commission rate (e.g., 0.001 = 0.1%)
        """
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.commission_rate = commission_rate
        self.open_positions: list[Trade] = []
        self.closed_trades: list[Trade] = []
        self._trade_counter = 0

    @property
    def positions_value(self) -> Decimal:
        """Calculate current value of open positions."""
        return sum(trade.entry_price * trade.quantity for trade in self.open_positions)

    @property
    def total_value(self) -> Decimal:
        """Calculate total portfolio value."""
        return self.cash + self.positions_value

    @property
    def returns(self) -> float:
        """Calculate portfolio returns."""
        return float((self.total_value - self.initial_capital) / self.initial_capital)

    @property
    def drawdown(self) -> float:
        """Calculate current drawdown."""
        peak_value = max(self.initial_capital, self.total_value)
        return float((self.total_value - peak_value) / peak_value)

    def buy(
        self,
        symbol: str,
        price: Decimal,
        quantity: Decimal,
        timestamp: datetime,
        stop_loss: Decimal | None = None,
        take_profit: Decimal | None = None,
    ) -> Trade:
        """Execute buy order.

        Args:
            symbol: Trading pair symbol
            price: Entry price
            quantity: Position size
            timestamp: Entry timestamp
            stop_loss: Stop loss price
            take_profit: Take profit price

        Returns:
            Created trade

        Raises:
            ValueError: If insufficient funds
        """
        # Calculate total cost including commission
        trade_value = price * quantity
        commission = trade_value * self.commission_rate
        total_cost = trade_value + commission

        if total_cost > self.cash:
            raise ValueError("Insufficient funds")

        # Create trade
        self._trade_counter += 1
        trade = Trade(
            id=f"trade_{self._trade_counter}",
            symbol=symbol,
            side="long",
            entry_price=price,
            quantity=quantity,
            entry_time=timestamp,
            stop_loss=stop_loss,
            take_profit=take_profit,
            status="open",
            entry_commission=commission,
        )

        # Update portfolio
        self.cash -= total_cost
        self.open_positions.append(trade)

        return trade

    def sell(
        self, trade_id: str, price: Decimal, timestamp: datetime, reason: str = "signal"
    ) -> Trade:
        """Execute sell order for existing position.

        Args:
            trade_id: Trade ID to close
            price: Exit price
            timestamp: Exit timestamp
            reason: Exit reason

        Returns:
            Closed trade

        Raises:
            ValueError: If trade not found
        """
        # Find trade
        trade = None
        for i, t in enumerate(self.open_positions):
            if t.id == trade_id:
                trade = self.open_positions.pop(i)
                break

        if not trade:
            raise ValueError(f"Trade not found: {trade_id}")

        # Calculate P&L
        exit_value = price * trade.quantity
        exit_commission = exit_value * self.commission_rate
        net_proceeds = exit_value - exit_commission

        entry_value = trade.entry_price * trade.quantity
        pnl = net_proceeds - entry_value - trade.entry_commission
        pnl_percent = float(pnl / entry_value) * 100

        # Update trade
        trade.exit_price = price
        trade.exit_time = timestamp
        trade.exit_commission = exit_commission
        trade.pnl = pnl
        trade.pnl_percent = pnl_percent
        trade.status = "closed"
        trade.exit_reason = reason
        trade.duration = timestamp - trade.entry_time

        # Update portfolio
        self.cash += net_proceeds
        self.closed_trades.append(trade)

        return trade

    def calculate_total_value(self, current_prices: dict[str, Decimal]) -> Decimal:
        """Calculate total portfolio value with current market prices.

        Args:
            current_prices: Current market prices by symbol

        Returns:
            Total portfolio value
        """
        positions_value = Decimal("0.0")

        for trade in self.open_positions:
            current_price = current_prices.get(trade.symbol, trade.entry_price)
            position_value = current_price * trade.quantity
            positions_value += position_value

        return self.cash + positions_value


class TradingStrategy:
    """Base class for trading strategies."""

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals from market data.

        Args:
            data: Market data DataFrame

        Returns:
            DataFrame with signals
        """
        raise NotImplementedError


class RSIStrategy(TradingStrategy):
    """RSI-based trading strategy."""

    def __init__(
        self,
        rsi_period: int = 14,
        oversold_threshold: int = 30,
        overbought_threshold: int = 70,
        stop_loss_pct: float = 0.02,
        take_profit_pct: float = 0.04,
    ):
        """Initialize RSI strategy.

        Args:
            rsi_period: RSI calculation period
            oversold_threshold: Oversold threshold for buy signals
            overbought_threshold: Overbought threshold for sell signals
            stop_loss_pct: Stop loss percentage
            take_profit_pct: Take profit percentage
        """
        self.rsi_period = rsi_period
        self.oversold_threshold = oversold_threshold
        self.overbought_threshold = overbought_threshold
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct

    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator.

        Args:
            prices: Price series (typically close prices)
            period: RSI period

        Returns:
            RSI values series
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate RSI-based trading signals.

        Args:
            data: Market data with OHLCV columns

        Returns:
            DataFrame with signals
        """
        # Calculate RSI if not present
        if "rsi" not in data.columns:
            data = data.copy()
            data["rsi"] = self.calculate_rsi(data["close"], self.rsi_period)

        signals = []

        for _, row in data.iterrows():
            rsi_value = row["rsi"]
            timestamp = row["timestamp"]

            if pd.isna(rsi_value):
                signal_type = "hold"
                strength = 0.0
                confidence = 0.5
            elif rsi_value <= self.oversold_threshold:
                signal_type = "buy"
                strength = (self.oversold_threshold - rsi_value) / self.oversold_threshold
                confidence = min(0.9, 0.5 + strength)
            elif rsi_value >= self.overbought_threshold:
                signal_type = "sell"
                strength = -(rsi_value - self.overbought_threshold) / (
                    100 - self.overbought_threshold
                )
                confidence = min(0.9, 0.5 + abs(strength))
            else:
                signal_type = "hold"
                strength = 0.0
                confidence = 0.5

            signals.append(
                {
                    "timestamp": timestamp,
                    "signal_type": signal_type,
                    "strength": strength,
                    "confidence": confidence,
                }
            )

        return pd.DataFrame(signals)

    def calculate_stop_loss(self, entry_price: Decimal, side: str = "long") -> Decimal:
        """Calculate stop loss price.

        Args:
            entry_price: Entry price
            side: Trade side (long/short)

        Returns:
            Stop loss price
        """
        if side == "long":
            return entry_price * Decimal(str(1 - self.stop_loss_pct))
        else:
            return entry_price * Decimal(str(1 + self.stop_loss_pct))

    def calculate_take_profit(self, entry_price: Decimal, side: str = "long") -> Decimal:
        """Calculate take profit price.

        Args:
            entry_price: Entry price
            side: Trade side (long/short)

        Returns:
            Take profit price
        """
        if side == "long":
            return entry_price * Decimal(str(1 + self.take_profit_pct))
        else:
            return entry_price * Decimal(str(1 - self.take_profit_pct))


class BacktestEngine:
    """Main backtesting engine."""

    def __init__(
        self,
        strategy: TradingStrategy,
        initial_capital: Decimal,
        commission_rate: Decimal = Decimal("0.001"),
    ):
        """Initialize backtest engine.

        Args:
            strategy: Trading strategy to test
            initial_capital: Starting capital
            commission_rate: Commission rate
        """
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.portfolio = Portfolio(initial_capital, commission_rate)

    def run_backtest(self, market_data: pd.DataFrame, symbol: str) -> "BacktestResult":
        """Run complete backtest.

        Args:
            market_data: Market data DataFrame
            symbol: Trading pair symbol

        Returns:
            Backtest result object
        """
        # Generate signals
        signals = self.strategy.generate_signals(market_data)

        # Process signals
        trades = self.process_signals(signals, market_data)

        # Calculate metrics
        from .models import BacktestResult

        result = BacktestResult(
            id=str(uuid.uuid4()),
            strategy_id=type(self.strategy).__name__,
            symbol=symbol,
            initial_capital=self.initial_capital,
            final_capital=self.portfolio.total_value,
            total_return=self.portfolio.returns,
            start_date=market_data["timestamp"].iloc[0],
            end_date=market_data["timestamp"].iloc[-1],
            total_trades=len(trades),
            win_rate=self._calculate_win_rate(),
            max_drawdown=self._calculate_max_drawdown(market_data),
        )

        return result

    def process_signals(self, signals: pd.DataFrame, market_data: pd.DataFrame) -> list[Trade]:
        """Process trading signals and execute trades.

        Args:
            signals: Trading signals DataFrame
            market_data: Market data DataFrame

        Returns:
            List of executed trades
        """
        executed_trades = []

        for i, signal_row in signals.iterrows():
            if signal_row["signal_type"] == "buy" and not self.portfolio.open_positions:
                # Enter long position
                market_row = market_data.iloc[i]
                price = Decimal(str(market_row["close"]))

                # Calculate position size (use 90% of available cash)
                available_cash = self.portfolio.cash * Decimal("0.9")
                quantity = (available_cash / price).quantize(
                    Decimal("0.001"), rounding=ROUND_HALF_UP
                )

                if quantity > 0:
                    # Calculate stop loss and take profit
                    stop_loss = None
                    take_profit = None

                    if isinstance(self.strategy, RSIStrategy):
                        stop_loss = self.strategy.calculate_stop_loss(price)
                        take_profit = self.strategy.calculate_take_profit(price)

                    try:
                        trade = self.portfolio.buy(
                            symbol=market_row.get("symbol", "BTC/USDT"),
                            price=price,
                            quantity=quantity,
                            timestamp=signal_row["timestamp"],
                            stop_loss=stop_loss,
                            take_profit=take_profit,
                        )
                        executed_trades.append(trade)
                    except ValueError:
                        # Insufficient funds
                        continue

            elif signal_row["signal_type"] == "sell" and self.portfolio.open_positions:
                # Close positions
                for trade in self.portfolio.open_positions.copy():
                    market_row = market_data.iloc[i]
                    price = Decimal(str(market_row["close"]))

                    closed_trade = self.portfolio.sell(
                        trade_id=trade.id,
                        price=price,
                        timestamp=signal_row["timestamp"],
                        reason="signal",
                    )
                    executed_trades.append(closed_trade)

            # Check stop loss and take profit for open positions
            if self.portfolio.open_positions:
                market_row = market_data.iloc[i]
                current_price = Decimal(str(market_row["close"]))

                for trade in self.portfolio.open_positions.copy():
                    # Check stop loss
                    if trade.stop_loss and current_price <= trade.stop_loss:
                        closed_trade = self.check_stop_loss(
                            trade, current_price, signal_row["timestamp"]
                        )
                        if closed_trade:
                            executed_trades.append(closed_trade)

                    # Check take profit
                    elif trade.take_profit and current_price >= trade.take_profit:
                        closed_trade = self.check_take_profit(
                            trade, current_price, signal_row["timestamp"]
                        )
                        if closed_trade:
                            executed_trades.append(closed_trade)

        return executed_trades

    def check_stop_loss(
        self, trade: Trade, current_price: Decimal, timestamp: datetime
    ) -> Trade | None:
        """Check and execute stop loss order.

        Args:
            trade: Open trade
            current_price: Current market price
            timestamp: Current timestamp

        Returns:
            Closed trade if stop loss triggered
        """
        if trade.stop_loss and current_price <= trade.stop_loss:
            return self.portfolio.sell(
                trade_id=trade.id,
                price=min(current_price, trade.stop_loss),
                timestamp=timestamp,
                reason="stop_loss",
            )
        return None

    def check_take_profit(
        self, trade: Trade, current_price: Decimal, timestamp: datetime
    ) -> Trade | None:
        """Check and execute take profit order.

        Args:
            trade: Open trade
            current_price: Current market price
            timestamp: Current timestamp

        Returns:
            Closed trade if take profit triggered
        """
        if trade.take_profit and current_price >= trade.take_profit:
            return self.portfolio.sell(
                trade_id=trade.id,
                price=max(current_price, trade.take_profit),
                timestamp=timestamp,
                reason="take_profit",
            )
        return None

    def _calculate_win_rate(self) -> float:
        """Calculate win rate from closed trades."""
        if not self.portfolio.closed_trades:
            return 0.0

        winning_trades = sum(1 for trade in self.portfolio.closed_trades if trade.pnl > 0)
        return winning_trades / len(self.portfolio.closed_trades)

    def _calculate_max_drawdown(self, market_data: pd.DataFrame) -> float:
        """Calculate maximum drawdown."""
        # Simplified calculation
        portfolio_values = []
        running_value = float(self.initial_capital)

        for trade in self.portfolio.closed_trades:
            if trade.pnl:
                running_value += float(trade.pnl)
                portfolio_values.append(running_value)

        if not portfolio_values:
            return 0.0

        peak = portfolio_values[0]
        max_dd = 0.0

        for value in portfolio_values:
            if value > peak:
                peak = value
            drawdown = (value - peak) / peak
            max_dd = min(max_dd, drawdown)

        return max_dd
