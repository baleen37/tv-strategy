#!/usr/bin/env python3
"""
Project structure validation script.
Checks that essential directories and files exist.
"""

import sys
from pathlib import Path


def check_project_structure() -> tuple[bool, list[str]]:
    """Check if project structure is valid."""
    errors = []
    root = Path(__file__).parent.parent

    # Required directories
    required_dirs = [
        "src",
        "src/backtest",
        "src/data",
        "src/strategies",
        "tests",
        "data",
    ]

    # Required files
    required_files = [
        "src/__init__.py",
        "src/main.py",
        "src/backtest/__init__.py",
        "src/backtest/engine.py",
        "src/backtest/models.py",
        "src/backtest/metrics.py",
        "src/data/__init__.py",
        "src/data/ccxt_client.py",
        "src/data/storage.py",
        "src/strategies/__init__.py",
        "src/strategies/validator.py",
        "tests/__init__.py",
        "requirements.txt",
        "Makefile",
        "README.md",
    ]

    # Check directories
    for dir_path in required_dirs:
        full_path = root / dir_path
        if not full_path.exists():
            errors.append(f"Missing directory: {dir_path}")
        elif not full_path.is_dir():
            errors.append(f"Path exists but is not a directory: {dir_path}")

    # Check files
    for file_path in required_files:
        full_path = root / file_path
        if not full_path.exists():
            errors.append(f"Missing file: {file_path}")
        elif not full_path.is_file():
            errors.append(f"Path exists but is not a file: {file_path}")

    # Check Pine Script strategies exist
    strategies_dir = root / "src" / "strategies"
    if strategies_dir.exists():
        pine_files = list(strategies_dir.glob("*.pine"))
        if not pine_files:
            errors.append("No Pine Script files found in src/strategies/")

    return len(errors) == 0, errors


def main() -> None:
    """Main entry point."""
    success, errors = check_project_structure()

    if success:
        print("✅ Project structure is valid")
        sys.exit(0)
    else:
        print("❌ Project structure validation failed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
