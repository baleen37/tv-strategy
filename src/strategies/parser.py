"""
Pine Script parser module - alias for validator module components.

This module provides aliases for the PineParser and SyntaxChecker
classes that are imported from the main validator module.
"""

from .validator import PineParser, SyntaxChecker

__all__ = ["PineParser", "SyntaxChecker"]
