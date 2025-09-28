"""
CCXT Client for cryptocurrency data collection.

Implements 5-level error recovery system with Binance API integration
as specified in research.md and required by TDD tests.
"""

import logging
import random
import time
from pathlib import Path

import ccxt
import pandas as pd

logger = logging.getLogger(__name__)


class CCXTError(Exception):
    """Custom exception for CCXT-related errors."""

    def __init__(self, message: str, error_level: int = 1, retry_suggested: bool = True):
        """Initialize CCXT error.

        Args:
            message: Error message
            error_level: Error severity level (1-5)
            retry_suggested: Whether retry is suggested
        """
        super().__init__(message)
        self.error_level = error_level
        self.retry_suggested = retry_suggested


class NetworkError(CCXTError):
    """Network-related errors (Level 1-2)."""

    pass


class AuthenticationError(CCXTError):
    """Authentication-related errors (Level 3)."""

    pass


class ExchangeError(CCXTError):
    """Exchange-specific errors (Level 4)."""

    pass


class DataQualityError(CCXTError):
    """Data quality validation errors (Level 5)."""

    pass


class CCXTClient:
    """CCXT client with Binance integration and error handling."""

    def __init__(self, exchange_name: str = "binance", sandbox: bool = False):
        """Initialize CCXT client.

        Args:
            exchange_name: Name of the exchange (default: binance)
            sandbox: Whether to use testnet/sandbox mode
        """
        self.exchange_name = exchange_name
        self.sandbox = sandbox

        try:
            exchange_class = getattr(ccxt, exchange_name)
            self.exchange = exchange_class(
                {
                    "sandbox": sandbox,
                    "rateLimit": 1200,  # Rate limiting
                    "enableRateLimit": True,
                    "timeout": 30000,  # 30 seconds timeout
                }
            )

            # Load markets
            self.exchange.load_markets()

        except Exception as e:
            raise CCXTError(f"Exchange unavailable: {str(e)}") from e

    def validate_symbol(self, symbol: str) -> bool:
        """Validate if symbol exists on exchange."""
        try:
            return symbol in self.exchange.markets
        except Exception:
            return False

    def download_data(self, symbol: str, timeframe: str, limit: int) -> pd.DataFrame:
        """Download OHLCV data with 5-level error recovery.

        5-Level Error Recovery System:
        Level 1: Network connectivity (retry with exponential backoff)
        Level 2: Rate limiting (wait and retry with jitter)
        Level 3: Authentication (refresh credentials)
        Level 4: Exchange-specific errors (fallback procedures)
        Level 5: Data quality validation (comprehensive checks)

        Args:
            symbol: Trading pair symbol (e.g., "BTC/USDT")
            timeframe: Timeframe (e.g., "1d", "4h")
            limit: Number of bars to download

        Returns:
            DataFrame with OHLCV data

        Raises:
            CCXTError: If data download fails after all recovery attempts
        """
        return self._download_with_recovery(symbol, timeframe, limit)

    def _download_with_recovery(self, symbol: str, timeframe: str, limit: int) -> pd.DataFrame:
        """Download data with 5-level error recovery."""
        max_retries = 5

        for attempt in range(max_retries):
            try:
                # Level 5: Pre-validate inputs
                self._validate_inputs(symbol, timeframe, limit)

                # Attempt data download
                ohlcv = self.exchange.fetch_ohlcv(symbol=symbol, timeframe=timeframe, limit=limit)

                if not ohlcv:
                    raise DataQualityError("Empty data returned from exchange", error_level=5)

                # Convert to DataFrame
                df = pd.DataFrame(
                    ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"]
                )

                # Convert timestamp to datetime
                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

                # Level 5: Data quality validation
                self._validate_data_quality(df, symbol, timeframe)

                logger.info(f"Successfully downloaded {len(df)} bars for {symbol} {timeframe}")
                return df

            except Exception as e:
                error_level = self._classify_error(e)
                logger.warning(
                    f"Attempt {attempt + 1}/{max_retries} failed with level {error_level} error: {str(e)}"
                )

                if attempt == max_retries - 1:
                    # Final attempt failed
                    raise CCXTError(
                        f"Data download failed after {max_retries} attempts: {str(e)}"
                    ) from e

                # Apply recovery strategy based on error level
                recovery_delay = self._apply_recovery_strategy(e, error_level, attempt)

                if recovery_delay > 0:
                    logger.info(
                        f"Applying recovery strategy: waiting {recovery_delay:.1f} seconds..."
                    )
                    time.sleep(recovery_delay)

    def _classify_error(self, error: Exception) -> int:
        """Classify error into 5-level system."""
        error_msg = str(error).lower()

        # Level 1: Network connectivity
        if any(
            keyword in error_msg for keyword in ["timeout", "connection", "network", "unreachable"]
        ):
            return 1

        # Level 2: Rate limiting
        if any(keyword in error_msg for keyword in ["rate limit", "too many requests", "429"]):
            return 2

        # Level 3: Authentication
        if any(
            keyword in error_msg
            for keyword in ["auth", "permission", "api key", "unauthorized", "401", "403"]
        ):
            return 3

        # Level 4: Exchange-specific errors
        if any(
            keyword in error_msg
            for keyword in ["invalid symbol", "invalid interval", "exchange", "market"]
        ):
            return 4

        # Level 5: Data quality issues
        if any(keyword in error_msg for keyword in ["data quality", "validation", "invalid data"]):
            return 5

        # Default to Level 1 for unknown errors
        return 1

    def _apply_recovery_strategy(self, error: Exception, error_level: int, attempt: int) -> float:
        """Apply recovery strategy based on error level.

        Returns:
            Delay in seconds before retry
        """
        base_delay = 2.0

        if error_level == 1:  # Network connectivity
            # Exponential backoff with jitter
            delay = base_delay * (2**attempt) + random.uniform(0, 1)
            logger.info(f"Level 1 recovery: exponential backoff ({delay:.1f}s)")
            return delay

        elif error_level == 2:  # Rate limiting
            # Longer delay with jitter to avoid synchronized retries
            delay = base_delay * 3 * (attempt + 1) + random.uniform(0, 5)
            logger.info(f"Level 2 recovery: rate limit backoff ({delay:.1f}s)")
            return delay

        elif error_level == 3:  # Authentication
            # Attempt to refresh connection
            try:
                logger.info("Level 3 recovery: refreshing exchange connection")
                self.exchange.load_markets()
                return base_delay
            except Exception as e:
                logger.error(f"Failed to refresh connection: {e}")
                return base_delay * 2

        elif error_level == 4:  # Exchange-specific
            # Try to reload markets and use shorter delay
            try:
                logger.info("Level 4 recovery: reloading markets")
                self.exchange.load_markets()
                return base_delay
            except Exception as e:
                logger.error(f"Failed to reload markets: {e}")
                return 0  # Don't retry exchange-specific errors multiple times

        elif error_level == 5:  # Data quality
            # Short delay, data quality issues are usually persistent
            logger.info("Level 5 recovery: minimal delay for data quality issues")
            return base_delay * 0.5

        return base_delay

    def _validate_inputs(self, symbol: str, timeframe: str, limit: int):
        """Validate inputs before making API calls."""
        if not symbol or not isinstance(symbol, str):
            raise DataQualityError("Invalid symbol provided", error_level=5, retry_suggested=False)

        if not timeframe or not isinstance(timeframe, str):
            raise DataQualityError(
                "Invalid timeframe provided", error_level=5, retry_suggested=False
            )

        if not isinstance(limit, int) or limit <= 0:
            raise DataQualityError("Invalid limit provided", error_level=5, retry_suggested=False)

        if limit > 1000:
            logger.warning(f"Large limit requested ({limit}), may hit API limits")

    def _validate_data_quality(self, df: pd.DataFrame, symbol: str, timeframe: str):
        """Comprehensive data quality validation."""
        if df.empty:
            raise DataQualityError("DataFrame is empty", error_level=5)

        # Check required columns
        required_columns = ["timestamp", "open", "high", "low", "close", "volume"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise DataQualityError(f"Missing columns: {missing_columns}", error_level=5)

        # Check for null values
        null_counts = df.isnull().sum()
        if null_counts.any():
            raise DataQualityError(f"Null values found: {null_counts.to_dict()}", error_level=5)

        # Check for negative prices or volumes
        price_columns = ["open", "high", "low", "close"]
        for col in price_columns:
            if (df[col] <= 0).any():
                raise DataQualityError(f"Invalid {col} prices (<=0) found", error_level=5)

        if (df["volume"] < 0).any():
            raise DataQualityError("Negative volume values found", error_level=5)

        # Check OHLC relationships
        invalid_ohlc = (
            (df["high"] < df["low"])
            | (df["high"] < df["open"])
            | (df["high"] < df["close"])
            | (df["low"] > df["open"])
            | (df["low"] > df["close"])
        )

        if invalid_ohlc.any():
            invalid_count = invalid_ohlc.sum()
            raise DataQualityError(
                f"Invalid OHLC relationships in {invalid_count} rows", error_level=5
            )

        # Check timestamp ordering
        if not df["timestamp"].is_monotonic_increasing:
            raise DataQualityError("Timestamps are not in ascending order", error_level=5)

        # Check for duplicate timestamps
        if df["timestamp"].duplicated().any():
            duplicate_count = df["timestamp"].duplicated().sum()
            raise DataQualityError(f"Duplicate timestamps found: {duplicate_count}", error_level=5)

        logger.info(f"Data quality validation passed for {symbol} {timeframe} ({len(df)} bars)")


class DataValidator:
    """Data validation functionality."""

    def validate_ohlcv(self, data: pd.DataFrame) -> bool:
        """Validate OHLCV data structure."""
        required_columns = ["timestamp", "open", "high", "low", "close", "volume"]
        return all(col in data.columns for col in required_columns)

    def validate_price_relationships(self, data: pd.DataFrame) -> bool:
        """Validate OHLC price relationships."""
        try:
            return (
                (data["high"] >= data["open"])
                & (data["high"] >= data["close"])
                & (data["high"] >= data["low"])
                & (data["low"] <= data["open"])
                & (data["low"] <= data["close"])
            ).all()
        except Exception:
            return False

    def detect_missing_data(self, data: pd.DataFrame, timeframe: str) -> int:
        """Detect missing data points."""
        try:
            # Convert timeframe to pandas frequency
            freq_map = {
                "1m": "1T",
                "5m": "5T",
                "15m": "15T",
                "1h": "1H",
                "4h": "4H",
                "1d": "1D",
                "1w": "1W",
            }

            freq = freq_map.get(timeframe, "1D")

            # Create expected date range
            start_date = data["timestamp"].min()
            end_date = data["timestamp"].max()
            expected_range = pd.date_range(start=start_date, end=end_date, freq=freq)

            # Count missing timestamps
            actual_timestamps = set(data["timestamp"])
            expected_timestamps = set(expected_range)

            return len(expected_timestamps - actual_timestamps)

        except Exception:
            return 0


class DataDownloader:
    """High-level data downloader interface."""

    def __init__(self, exchange: str = "binance", data_dir: str = "data/"):
        """Initialize data downloader.

        Args:
            exchange: Exchange name
            data_dir: Directory to save data files
        """
        self.exchange_name = exchange
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        self.client = CCXTClient(exchange)

    def download(self, symbol: str, timeframe: str, limit: int) -> Path:
        """Download data and save to file.

        Args:
            symbol: Trading pair symbol
            timeframe: Timeframe
            limit: Number of bars

        Returns:
            Path to saved data file
        """
        # Download data
        data = self.client.download_data(symbol, timeframe, limit)

        # Import storage here to avoid circular imports
        from .storage import ParquetStorage

        # Save data
        storage = ParquetStorage(data_dir=self.data_dir)
        file_path = storage.save(data, symbol.replace("/", ""), timeframe, limit)

        return file_path


def download_command(args: list[str]) -> int:
    """CLI command for data download.

    Args:
        args: Command line arguments [symbol, timeframe, limit]

    Returns:
        Exit code (0 for success)
    """
    try:
        if len(args) != 3:
            raise ValueError("Invalid arguments: Expected [symbol, timeframe, limit]")

        symbol, timeframe, limit_str = args

        # Validate timeframe
        valid_timeframes = ["1m", "5m", "15m", "1h", "4h", "1d", "1w"]
        if timeframe not in valid_timeframes:
            raise ValueError(f"Invalid timeframe: {timeframe}")

        # Validate limit
        try:
            limit = int(limit_str)
            if limit <= 0:
                raise ValueError("Limit must be positive")
        except ValueError as e:
            raise ValueError(f"Invalid limit: {limit_str}") from e

        # Add slash to symbol if not present
        if "/" not in symbol:
            symbol = f"{symbol[:3]}/{symbol[3:]}"  # e.g., BTCUSDT -> BTC/USDT

        # Download data
        downloader = DataDownloader()
        file_path = downloader.download(symbol, timeframe, limit)

        print(f"Data downloaded successfully: {file_path}")
        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "download":
        exit_code = download_command(sys.argv[2:])
        sys.exit(exit_code)
    else:
        print("Usage: python -m src.data.ccxt_client download SYMBOL TIMEFRAME LIMIT")
        sys.exit(1)
