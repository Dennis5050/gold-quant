# backend/core/__init__.py

"""
Core package.

Modules:
- regime_detector: detect market regimes (Trend / Range / Chaos)
- feature_engineer: calculate features like Z-score, ATR, volatility %
- beta_calculator: calculate Gold vs DXY beta
- signal_generator: generate buy/sell/flat signals
- validator: strict logic gate ensuring all conditions met
"""

from .regime_detector import RegimeDetector
from .feature_engineer import FeatureEngineer
from .beta_calculator import BetaCalculator
from .signal_generator import SignalGenerator
from .validator import Validator

__all__ = [
    "RegimeDetector",
    "FeatureEngineer",
    "BetaCalculator",
    "SignalGenerator",
    "Validator"
]
