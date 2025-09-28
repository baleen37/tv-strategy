"""
Strategy analyzer module - alias for validator module components.

This module provides aliases for the StrategyAnalyzer and IndicatorValidator
classes that are imported from the main validator module.
"""

from .validator import IndicatorValidator, StrategyAnalyzer

__all__ = ["StrategyAnalyzer", "IndicatorValidator"]
