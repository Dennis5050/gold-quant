# backend/execution/__init__.py

"""
Execution module for Gold-Quant system.

This module handles order execution, trade logging, and virtual/backtest simulation.
It includes:
- mt5_executor.py : real/paper MT5 order sending
- virtual_broker.py : backtest or paper trade simulation
- trade_logger.py : logging trades and rejected orders
"""

__all__ = [
    "mt5_executor",
    "virtual_broker",
    "trade_logger"
]
