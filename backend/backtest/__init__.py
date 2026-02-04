# backend/backtest/__init__.py

"""
Backtesting package for gold-quant.

Modules included:
- backtester.py        : Candle-by-candle simulation engine
- walk_forward.py      : Walk-forward validation loop
- performance_audit.py : Metrics (PF, DD, expectancy, WFE)
"""

from .backtester import Backtester
from .performance_audit import PerformanceAudit
