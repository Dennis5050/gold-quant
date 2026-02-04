# backend/execution/mt5_executor.py

import random
import time
import logging

class MT5Executor:
    """
    Simplified MT5 order executor.
    Can simulate paper trades or interface with real MT5 orders.
    """

    def __init__(self, mode="paper"):
        """
        mode: "paper" or "live"
        """
        self.mode = mode
        self.logger = logging.getLogger("MT5Executor")

    def send_order(self, symbol, direction, volume, price=None, sl=None, tp=None):
        """
        direction: 1 = BUY, -1 = SELL
        volume: number of contracts
        price: entry price (optional for paper mode)
        sl: stop loss
        tp: take profit
        """
        if self.mode == "paper":
            return self._simulate_order(symbol, direction, volume, price, sl, tp)
        else:
            # In future, integrate with MT5 API here
            raise NotImplementedError("Live mode not implemented yet")

    def _simulate_order(self, symbol, direction, volume, price, sl, tp):
        """
        Simulate execution with slippage and PnL.
        """
        # 1. Fake market price if not provided
        market_price = price or self._get_market_price(symbol)
        
        # 2. Apply slippage (random 0-0.02%)
        slippage = market_price * random.uniform(-0.0002, 0.0002)
        executed_price = market_price + slippage

        # 3. Log the simulated trade
        self.logger.info(
            f"[SIM] {symbol} | {'BUY' if direction==1 else 'SELL'} | "
            f"Volume: {volume} | Price: {executed_price:.2f} | SL: {sl} | TP: {tp}"
        )

        # 4. Return simulated trade data
        trade = {
            "symbol": symbol,
            "direction": direction,
            "volume": volume,
            "entry_price": executed_price,
            "sl": sl,
            "tp": tp,
            "status": "executed",
            "timestamp": time.time()
        }
        return trade

    def _get_market_price(self, symbol):
        """
        Mock market price for paper mode.
        In production, fetch real-time quotes from MT5.
        """
        base_prices = {"XAUUSD": 1900, "DXY": 102}
        return base_prices.get(symbol, 100)
