# backend/execution/__init__.py

"""
Execution package.

Modules:
- mt5_executor: handles live/paper order execution
- virtual_broker: backtest or paper trade simulation
- trade_logger: logging trades and rejections
"""

from .mt5_executor import MT5Executor
from .virtual_broker import VirtualBroker
from .trade_logger import TradeLogger

__all__ = [
    "MT5Executor",
    "VirtualBroker",
    "TradeLogger"
]
