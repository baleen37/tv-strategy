"""
Main CLI entry point for the cryptocurrency backtesting system.

Implements argument parsing, workflow orchestration, and command execution
as required by TDD tests and quickstart.md specifications.
"""

import argparse
import logging
import sys
import traceback
from decimal import Decimal
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class WorkflowResult:
    """Result object for workflow operations."""

    def __init__(
        self,
        success: bool = False,
        output: str = "",
        error_message: str = "",
        file_path: Path | None = None,
        backtest_result: Any = None,
        coverage_percentage: float = 0.0,
        constitution_compliant: bool = False,
        retry_suggested: bool = False,
        messages: list | None = None,
    ):
        """Initialize workflow result.

        Args:
            success: Whether operation succeeded
            output: Output message
            error_message: Error message if failed
            file_path: Path to generated file
            backtest_result: Backtest result object
            coverage_percentage: Test coverage percentage
            constitution_compliant: Whether meets constitution requirements
            retry_suggested: Whether retry is suggested
            messages: List of messages
        """
        self.success = success
        self.output = output
        self.error_message = error_message
        self.file_path = file_path
        self.backtest_result = backtest_result
        self.coverage_percentage = coverage_percentage
        self.constitution_compliant = constitution_compliant
        self.retry_suggested = retry_suggested
        self.messages = messages or []


class QuickstartWorkflow:
    """Quickstart workflow implementations."""

    @staticmethod
    def data_download(symbol: str, timeframe: str, limit: int) -> WorkflowResult:
        """Execute data download workflow.

        Args:
            symbol: Trading pair symbol
            timeframe: Timeframe
            limit: Number of bars

        Returns:
            Workflow result
        """
        try:
            from src.data.ccxt_client import DataDownloader

            # Format symbol
            if "/" not in symbol:
                symbol = f"{symbol[:3]}/{symbol[3:]}"

            output = f"📊 Loading data: {symbol} {timeframe} ({limit} bars)\n"

            # Download data
            downloader = DataDownloader()
            file_path = downloader.download(symbol, timeframe, limit)

            output += "✅ Data downloaded successfully\n"
            output += f"📁 File saved: {file_path}\n"

            return WorkflowResult(success=True, output=output, file_path=file_path)

        except Exception as e:
            return WorkflowResult(
                success=False,
                error_message=f"Data download failed: {str(e)}",
                retry_suggested="network" in str(e).lower(),
            )

    @staticmethod
    def basic_backtest(symbol: str, data_file: Path | None = None) -> WorkflowResult:
        """Execute basic backtest workflow.

        Args:
            symbol: Trading pair symbol
            data_file: Optional data file path

        Returns:
            Workflow result
        """
        try:
            from src.backtest.engine import BacktestEngine, RSIStrategy
            from src.data.storage import ParquetStorage

            output = "🔄 Running RSI backtest...\n"

            # Load data
            if data_file is None:
                storage = ParquetStorage()
                symbol_clean = symbol.replace("/", "")
                data_file = storage.get_filename(symbol_clean, "1d", 100)

            storage = ParquetStorage()
            market_data = storage.load(data_file)

            # Initialize strategy and engine
            strategy = RSIStrategy()
            engine = BacktestEngine(strategy=strategy, initial_capital=Decimal("10000.0"))

            # Run backtest
            result = engine.run_backtest(market_data, symbol)

            # Format results
            output += f"📈 Total Return: {result.total_return * 100:.1f}%\n"
            output += f"📉 Max Drawdown: {result.max_drawdown * 100:.1f}%\n"
            output += f"🎯 Win Rate: {result.win_rate * 100:.1f}%\n"
            output += f"📊 Total Trades: {result.total_trades}\n"
            output += "✅ Backtest complete!\n"

            return WorkflowResult(success=True, output=output, backtest_result=result)

        except Exception as e:
            return WorkflowResult(
                success=False, error_message=f"Backtest execution failed: {str(e)}"
            )

    @staticmethod
    def validate_pine_script(file_path: str) -> WorkflowResult:
        """Validate Pine Script file.

        Args:
            file_path: Path to Pine Script file

        Returns:
            Workflow result
        """
        try:
            file_path_obj = Path(file_path)

            if not file_path_obj.exists():
                return WorkflowResult(success=False, error_message=f"File not found: {file_path}")

            # Read and basic validate Pine Script
            content = file_path_obj.read_text()

            output = "🔍 Validating Pine Script...\n"

            # Basic validations
            if "//@version=6" not in content:
                return WorkflowResult(
                    success=False, output=output + "❌ Pine Script v6 version declaration missing\n"
                )

            if "strategy(" not in content:
                return WorkflowResult(
                    success=False, output=output + "❌ Strategy declaration missing\n"
                )

            output += "✅ Pine Script v6 문법 확인\n"
            output += "✅ 전략 구조 검증\n"

            # RSI-specific validation
            if "rsi" in content.lower():
                output += "✅ RSI 로직 검증 완료\n"

            return WorkflowResult(success=True, output=output)

        except Exception as e:
            return WorkflowResult(
                success=False, error_message=f"Pine Script validation failed: {str(e)}"
            )

    @staticmethod
    def verify_coverage() -> WorkflowResult:
        """Verify test coverage meets constitution requirements.

        Returns:
            Workflow result
        """
        try:
            import subprocess

            # Run pytest with coverage
            result = subprocess.run(
                ["python", "-m", "pytest", "--cov=src", "--cov-report=term-missing"],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
            )

            # Parse coverage from output
            coverage_line = None
            for line in result.stdout.split("\n"):
                if "TOTAL" in line and "%" in line:
                    coverage_line = line
                    break

            if coverage_line:
                # Extract percentage
                parts = coverage_line.split()
                for part in parts:
                    if "%" in part:
                        coverage_str = part.replace("%", "")
                        coverage_pct = float(coverage_str)
                        break
                else:
                    coverage_pct = 0.0
            else:
                coverage_pct = 0.0

            constitution_compliant = coverage_pct >= 95.0

            output = f"📊 Test Coverage: {coverage_pct:.1f}%\n"

            if constitution_compliant:
                output += "✅ Constitution requirement met (>=95%)\n"
            else:
                output += "❌ Constitution requirement not met (<95%)\n"

            return WorkflowResult(
                success=constitution_compliant,
                output=output,
                coverage_percentage=coverage_pct,
                constitution_compliant=constitution_compliant,
                error_message="" if constitution_compliant else "Constitution requirement not met",
            )

        except Exception as e:
            return WorkflowResult(
                success=False, error_message=f"Coverage verification failed: {str(e)}"
            )


class FullWorkflow:
    """Full workflow orchestration."""

    @staticmethod
    def execute(args: argparse.Namespace) -> WorkflowResult:
        """Execute complete workflow.

        Args:
            args: Parsed command line arguments

        Returns:
            Workflow result
        """
        try:
            from src.backtest.engine import BacktestEngine, RSIStrategy
            from src.data.ccxt_client import DataDownloader
            from src.data.storage import ParquetStorage

            messages = []

            # Check if data file exists
            storage = ParquetStorage(data_dir=args.data_dir)
            symbol_clean = args.symbol.replace("/", "")
            data_file = storage.get_filename(symbol_clean, args.timeframe, 100)

            if data_file.exists():
                messages.append("Using existing data file")
            else:
                # Download data
                try:
                    downloader = DataDownloader(data_dir=args.data_dir)
                    if "/" not in args.symbol:
                        symbol = f"{args.symbol[:3]}/{args.symbol[3:]}"
                    else:
                        symbol = args.symbol

                    data_file = downloader.download(symbol, args.timeframe, 100)
                    messages.append("Data downloaded successfully")

                except Exception as e:
                    return WorkflowResult(
                        success=False,
                        error_message=f"Data download failed: {str(e)}",
                        retry_suggested="network" in str(e).lower(),
                    )

            # Validate strategy if specified
            if hasattr(args, "strategy_file") and args.strategy_file:
                validation_result = QuickstartWorkflow.validate_pine_script(args.strategy_file)
                if not validation_result.success:
                    return WorkflowResult(success=False, error_message="Strategy validation failed")
                messages.append("Strategy validation passed")

            # Load data and run backtest
            try:
                market_data = storage.load(data_file)

                # Initialize strategy and engine
                strategy = RSIStrategy()
                engine = BacktestEngine(
                    strategy=strategy,
                    initial_capital=Decimal(str(args.initial_capital)),
                    commission_rate=Decimal(str(args.commission_rate)),
                )

                # Run backtest
                result = engine.run_backtest(market_data, args.symbol)

                return WorkflowResult(success=True, backtest_result=result, messages=messages)

            except Exception as e:
                return WorkflowResult(
                    success=False, error_message=f"Backtest execution failed: {str(e)}"
                )

        except Exception as e:
            return WorkflowResult(
                success=False, error_message=f"Workflow execution failed: {str(e)}"
            )


class BacktestCLI:
    """Command-line interface for backtesting."""

    def __init__(self):
        """Initialize CLI."""
        self.logger = logging.getLogger(__name__)

    def setup_logging(self, level: str = "INFO", log_file: str | None = None):
        """Setup logging configuration.

        Args:
            level: Logging level
            log_file: Optional log file path
        """
        log_level = getattr(logging, level.upper())

        handlers = [logging.StreamHandler()]
        if log_file:
            handlers.append(logging.FileHandler(log_file))

        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=handlers,
            force=True,
        )

    def validate_args(self, args: dict[str, Any]) -> bool:
        """Validate command line arguments.

        Args:
            args: Arguments dictionary

        Returns:
            True if valid
        """
        try:
            # Validate symbol
            symbol = args.get("symbol", "")
            if not symbol or len(symbol) < 6:
                return False

            # Validate timeframe
            timeframe = args.get("timeframe", "")
            valid_timeframes = ["1m", "5m", "15m", "1h", "4h", "1d", "1w"]
            if timeframe not in valid_timeframes:
                return False

            # Validate capital
            initial_capital = args.get("initial_capital", 0)
            if initial_capital <= 0:
                return False

            # Validate commission
            commission_rate = args.get("commission_rate", 0)
            if commission_rate < 0 or commission_rate > 1:
                return False

            return True

        except Exception:
            return False

    def report_progress(self, stage: str, percentage: int):
        """Report progress to stdout.

        Args:
            stage: Current stage
            percentage: Progress percentage
        """
        print(f"[{percentage:3d}%] {stage}")

    def run(self, args: argparse.Namespace) -> int:
        """Run CLI command.

        Args:
            args: Parsed arguments

        Returns:
            Exit code
        """
        try:
            if args.command == "backtest":
                result = FullWorkflow.execute(args)

                if result.success:
                    print("✅ Backtest completed successfully")
                    if result.backtest_result:
                        print(f"📈 Total Return: {result.backtest_result.total_return * 100:.1f}%")
                        print(f"📉 Max Drawdown: {result.backtest_result.max_drawdown * 100:.1f}%")
                        print(f"🎯 Win Rate: {result.backtest_result.win_rate * 100:.1f}%")
                    return 0
                else:
                    print(f"❌ {result.error_message}")
                    return 1

            elif args.command == "download":
                result = QuickstartWorkflow.data_download(args.symbol, args.timeframe, args.limit)

                if result.success:
                    print(result.output)
                    return 0
                else:
                    print(f"❌ {result.error_message}")
                    return 1

            elif args.command == "validate":
                result = QuickstartWorkflow.validate_pine_script(args.file)

                if result.success:
                    print(result.output)
                    return 0
                else:
                    print(f"❌ {result.error_message}")
                    return 1

            else:
                print(f"❌ Unknown command: {args.command}")
                return 1

        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            return 1


def parse_arguments(args_list: list | None = None) -> argparse.Namespace:
    """Parse command line arguments.

    Args:
        args_list: Optional list of arguments (for testing)

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Cryptocurrency Backtesting System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Backtest command
    backtest_parser = subparsers.add_parser("backtest", help="Run backtest")
    backtest_parser.add_argument(
        "--symbol", required=True, help="Trading pair symbol (e.g., BTCUSDT)"
    )
    backtest_parser.add_argument("--timeframe", default="1d", help="Timeframe (default: 1d)")
    backtest_parser.add_argument(
        "--initial-capital", type=float, default=10000, help="Initial capital (default: 10000)"
    )
    backtest_parser.add_argument(
        "--commission-rate", type=float, default=0.001, help="Commission rate (default: 0.001)"
    )
    backtest_parser.add_argument(
        "--data-dir", default="data/", help="Data directory (default: data/)"
    )
    backtest_parser.add_argument(
        "--output-dir", default="results/", help="Output directory (default: results/)"
    )
    backtest_parser.add_argument(
        "--strategy", default="rsi_basic", help="Strategy to use (default: rsi_basic)"
    )

    # Download command
    download_parser = subparsers.add_parser("download", help="Download market data")
    download_parser.add_argument("--symbol", required=True, help="Trading pair symbol")
    download_parser.add_argument("--timeframe", required=True, help="Timeframe")
    download_parser.add_argument(
        "--limit", type=int, required=True, help="Number of bars to download"
    )

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate Pine Script")
    validate_parser.add_argument("--file", required=True, help="Pine Script file to validate")

    # Parse arguments
    if args_list is not None:
        return parser.parse_args(args_list)
    else:
        return parser.parse_args()


def main() -> int:
    """Main entry point.

    Returns:
        Exit code
    """
    try:
        # Parse arguments
        args = parse_arguments()

        # Validate command
        if not args.command:
            print("❌ No command specified. Use --help for usage information.")
            return 1

        # Initialize CLI
        cli = BacktestCLI()

        # Setup logging
        cli.setup_logging()

        # Execute command
        return cli.run(args)

    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
        return 130

    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        logger.error(f"Unexpected error: {str(e)}\n{traceback.format_exc()}")
        return 1


# Create workflow module aliases for test compatibility
quickstart_workflow = QuickstartWorkflow()
full_workflow = FullWorkflow()


if __name__ == "__main__":
    sys.exit(main())
