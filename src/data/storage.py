"""
Data storage functionality for Parquet file operations.

Implements storage, loading, and validation for OHLCV data
as required by TDD tests.
"""

import logging
import os
from pathlib import Path
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


class ParquetStorage:
    """Parquet file storage for OHLCV data."""

    def __init__(self, data_dir: str | Path = "data/", compression: str = "snappy"):
        """Initialize Parquet storage.

        Args:
            data_dir: Directory to store data files
            compression: Compression algorithm (snappy, gzip, brotli)
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.compression = compression

    def save(self, data: pd.DataFrame, symbol: str, timeframe: str, limit: int) -> Path:
        """Save DataFrame to Parquet file.

        Args:
            data: OHLCV DataFrame to save
            symbol: Trading pair symbol (without slash)
            timeframe: Timeframe (e.g., "1d", "4h")
            limit: Number of bars

        Returns:
            Path to saved file

        Raises:
            IOError: If disk space or permission issues
        """
        try:
            file_path = self.get_filename(symbol, timeframe, limit)

            # Check available disk space (basic check)
            self._check_disk_space(file_path.parent)

            # Save with compression
            data.to_parquet(file_path, compression=self.compression, index=False)

            logger.info(f"Data saved to {file_path}")
            return file_path

        except OSError as e:
            if "No space left" in str(e):
                raise OSError("No space left on device") from e
            else:
                raise OSError(f"Failed to save data: {str(e)}") from e

    def load(self, file_path: str | Path) -> pd.DataFrame:
        """Load DataFrame from Parquet file.

        Args:
            file_path: Path to Parquet file

        Returns:
            Loaded DataFrame

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is corrupted
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Data file not found: {file_path}")

        try:
            data = pd.read_parquet(file_path)

            # Basic validation
            if data.empty:
                raise ValueError("Loaded data is empty")

            return data

        except Exception as e:
            raise ValueError(f"Failed to load data: {str(e)}") from e

    def get_filename(self, symbol: str, timeframe: str, limit: int) -> Path:
        """Get standardized filename for data file.

        Args:
            symbol: Trading pair symbol
            timeframe: Timeframe
            limit: Number of bars

        Returns:
            Path object for the file
        """
        filename = f"{symbol}_{timeframe}_{limit}.parquet"
        return self.data_dir / filename

    def _check_disk_space(self, directory: Path) -> None:
        """Check available disk space.

        Args:
            directory: Directory to check

        Raises:
            IOError: If insufficient disk space
        """
        try:
            # Check disk space (simplified)
            statvfs = os.statvfs(directory)
            available_bytes = statvfs.f_frsize * statvfs.f_bavail

            # Require at least 100MB free
            min_free_bytes = 100 * 1024 * 1024

            if available_bytes < min_free_bytes:
                raise OSError("Insufficient disk space")

        except AttributeError:
            # os.statvfs not available on Windows
            pass
        except Exception as e:
            logger.warning(f"Could not check disk space: {e}")


class DataStorage(ParquetStorage):
    """Alias for ParquetStorage to match test expectations."""

    def save_to_parquet(self, data: pd.DataFrame, symbol: str, timeframe: str, limit: int) -> Path:
        """Save data to Parquet (alias for save method)."""
        return self.save(data, symbol, timeframe, limit)

    def load_from_parquet(self, file_path: str | Path) -> pd.DataFrame:
        """Load data from Parquet (alias for load method)."""
        return self.load(file_path)


class DataValidator:
    """Data validation functionality for testing compatibility."""

    @staticmethod
    def validate_ohlcv_data(df: pd.DataFrame) -> bool:
        """Validate OHLCV data format and quality."""
        try:
            # Check required columns
            required_columns = ["timestamp", "open", "high", "low", "close", "volume"]
            if not all(col in df.columns for col in required_columns):
                return False

            # Check for empty data
            if df.empty:
                return False

            # Check for null values
            if df.isnull().any().any():
                return False

            # Check OHLC relationships
            price_valid = (
                (df["high"] >= df["open"])
                & (df["high"] >= df["close"])
                & (df["high"] >= df["low"])
                & (df["low"] <= df["open"])
                & (df["low"] <= df["close"])
                & (df["open"] > 0)
                & (df["high"] > 0)
                & (df["low"] > 0)
                & (df["close"] > 0)
            ).all()

            # Check for non-negative volume
            volume_valid = (df["volume"] >= 0).all()

            return price_valid and volume_valid

        except Exception:
            return False

    @staticmethod
    def validate_data_integrity(file_path: str | Path) -> dict[str, Any]:
        """Validate data file integrity."""
        file_path = Path(file_path)

        result = {
            "file_exists": file_path.exists(),
            "file_size": file_path.stat().st_size if file_path.exists() else 0,
            "is_valid_format": False,
            "row_count": 0,
            "errors": [],
        }

        try:
            if result["file_exists"]:
                df = pd.read_parquet(file_path)
                result["row_count"] = len(df)
                result["is_valid_format"] = DataValidator.validate_ohlcv_data(df)

        except Exception as e:
            result["errors"].append(str(e))

        return result
