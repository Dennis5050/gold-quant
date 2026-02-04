# backend/risk/__init__.py

"""
Risk management package.

Modules:
- risk_manager: position sizing, stop-loss/take-profit calculation
- kill_switch: system-level checks for drawdown and expectancy
- regime_auditor: optional: adjust risk based on market regime
"""

from .risk_manager import RiskManager
from .kill_switch import KillSwitch
from .regime_auditor import RegimeAuditor  # make sure this class exists in regime_auditor.py

__all__ = [
    "RiskManager",
    "KillSwitch",
    "RegimeAuditor"
]
