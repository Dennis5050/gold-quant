# backend/backtest/backtester.py

import pandas as pd
import numpy as np
import logging
from datetime import datetime
from core.signal_generator import SignalGenerator
from risk.risk_manager import RiskManager
from risk.kill_switch import KillSwitch
from execution.mt5_executor import MT5Executor

class Backtester:
    def __init__(self, df, account_equity=100000, risk_per_trade=0.01, mode="paper"):
        """
        df: DataFrame containing OHLC + indicators
        account_equity: starting capital
        risk_per_trade: fraction of equity per trade
        mode: "paper" or "live" (for MT5Executor)
        """
        self.df = df.copy()
        self.equity = account_equity
        self.risk_manager = RiskManager(account_equity, risk_per_trade)
        self.kill_switch = KillSwitch()
        self.executor = MT5Executor(mode=mode)
        self.signals = SignalGenerator()
        self.trades = []
        self.kill_switch.reset(self.equity)

        # Logging
        self.logger = logging.getLogger("Backtester")
        handler = logging.FileHandler("backend/logs/backtest.log")
        handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def run(self):
        """
        Candle-by-candle backtest.
        """
        for i, row in self.df.iterrows():
            signal = self.signals.generate_signal(row)
            
            if signal == 0:
                continue  # no trade
            
            # Determine position size
            atr = row.get("atr", 1)  # fallback ATR
            entry_price = row["xau_close"]
            stop_loss, take_profit = self.risk_manager.apply_sl_tp(
                entry_price, signal, atr
            )
            size = self.risk_manager.calculate_position_size(entry_price, stop_loss)

            # Kill switch check
            if not self.kill_switch.is_system_active(self.equity, expectancy=0.15):
                self.logger.info("Kill switch triggered, stopping backtest.")
                break

            # Execute trade (paper mode)
            trade = self.executor.send_order(
                symbol="XAUUSD",
                direction=signal,
                volume=size,
                price=entry_price,
                sl=stop_loss,
                tp=take_profit
            )
            
            # Update equity (simplified PnL calculation)
            pnl = self._calculate_pnl(trade)
            self.equity += pnl

            self.trades.append(trade)
            self.logger.info(f"Trade executed: {trade} | PnL: {pnl:.2f} | Equity: {self.equity:.2f}")

        return pd.DataFrame(self.trades)

    def _calculate_pnl(self, trade):
        """
        Simplified PnL calculation: closes at TP/SL with fixed outcome.
        In full version, use candle-by-candle price movement.
        """
        direction = trade["direction"]
        entry = trade["entry_price"]
        sl = trade["sl"]
        tp = trade["tp"]

        # Simulate hitting TP 50%, SL 30%, otherwise flat
        rnd = np.random.rand()
        if rnd < 0.5:
            exit_price = tp
        elif rnd < 0.8:
            exit_price = sl
        else:
            exit_price = entry  # no move

        pnl = (exit_price - entry) * direction * trade["volume"]
        return pnl
