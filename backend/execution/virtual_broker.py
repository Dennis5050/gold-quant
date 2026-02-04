# backend/execution/virtual_broker.py

import logging
from .mt5_executor import MT5Executor

class VirtualBroker:
    """
    Simulated broker for backtesting and paper trading.
    Wraps MT5Executor and manages multiple trades.
    """

    def __init__(self, mode="paper"):
        self.executor = MT5Executor(mode=mode)
        self.logger = logging.getLogger("VirtualBroker")
        self.active_trades = []

    def place_trade(self, symbol, direction, volume, price=None, sl=None, tp=None):
        """
        Place a single trade via MT5Executor.
        Stores trade in active_trades list.
        """
        trade = self.executor.send_order(symbol, direction, volume, price, sl, tp)
        self.active_trades.append(trade)
        self.logger.info(f"Trade placed: {trade}")
        return trade

    def close_trade(self, trade, exit_price=None):
        """
        Close a specific trade.
        """
        trade['exit_price'] = exit_price or trade['entry_price']
        trade['status'] = "closed"
        self.logger.info(f"Trade closed: {trade}")
        # Remove from active trades
        self.active_trades = [t for t in self.active_trades if t != trade]

    def close_all_trades(self, exit_prices=None):
        """
        Close all active trades. Optionally provide a dict of exit_prices keyed by symbol.
        """
        for trade in self.active_trades.copy():
            price = exit_prices.get(trade['symbol']) if exit_prices else None
            self.close_trade(trade, exit_price=price)

    def get_open_trades(self):
        """
        Return a list of currently active trades.
        """
        return self.active_trades

    def summary(self):
        """
        Simple summary of trades: open, closed, PnL (simulated)
        """
        open_count = len(self.active_trades)
        closed_count = sum(1 for t in self.active_trades if t.get('status') == 'closed')
        self.logger.info(f"Open trades: {open_count}, Closed trades: {closed_count}")
        return {
            "open_trades": open_count,
            "closed_trades": closed_count
        }
