# backend/execution/virtual_broker.py

import pandas as pd
from .mt5_executor import MT5Executor
from risk.risk_manager import RiskManager
from risk.kill_switch import KillSwitch
import logging
import time

class VirtualBroker:
    """
    Simulated broker for backtesting and paper trading.
    Integrates RiskManager, KillSwitch, and MT5Executor.
    """

    def __init__(self, initial_equity=100000, risk_per_trade=0.01):
        self.equity = initial_equity
        self.risk_manager = RiskManager(account_equity=initial_equity, risk_per_trade=risk_per_trade)
        self.kill_switch = KillSwitch()
        self.kill_switch.reset(initial_equity)
        self.executor = MT5Executor(mode="paper")
        self.trades = []  # store trade history
        self.logger = logging.getLogger("VirtualBroker")

    def place_trade(self, symbol, direction, price, atr):
        """
        Place a trade with risk management and kill switch checks.
        direction: 1 = LONG, -1 = SHORT
        price: entry price
        atr: used for SL/TP calculation
        """
        if not self.kill_switch.is_system_active(self.equity, expectancy=0.2):
            self.logger.warning("Kill switch triggered, no trades allowed")
            return None

        # Calculate SL and TP
        sl, tp = self.risk_manager.apply_sl_tp(price, direction, atr)

        # Calculate position size
        size = self.risk_manager.calculate_position_size(price, sl)
        if size == 0:
            self.logger.warning("Position size zero, skipping trade")
            return None

        # Execute trade
        trade = self.executor.send_order(symbol, direction, size, price, sl, tp)

        # Log trade and update equity for simulation
        self.trades.append(trade)

        # For simplicity, assume we lock risk per trade and update equity instantly
        # In real backtest, PnL would be calculated when trade closes
        self.logger.info(f"Trade executed: {trade}")
        return trade

    def get_trade_history(self):
        """Return a DataFrame of all executed trades"""
        return pd.DataFrame(self.trades)

    def reset(self):
        """Reset broker state for new backtest"""
        self.equity = self.risk_manager.equity
        self.kill_switch.reset(self.equity)
        self.trades = []
