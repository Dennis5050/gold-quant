# backend/backtest/performance_audit.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class PerformanceAudit:
    """
    Enhanced backtest performance audit.
    Metrics:
    - Profit Factor (PF)
    - Max Drawdown (DD) in %
    - Expectancy (average R-multiple)
    - Walk-Forward Efficiency (WFE)
    - Equity curve plotting
    """

    def __init__(self, trades: pd.DataFrame, commission_per_trade=0, slippage_pct=0.0):
        """
        trades: DataFrame with columns:
            - 'entry_price', 'exit_price', 'direction' (1=LONG, -1=SHORT), 'size'
        commission_per_trade: fixed cost per trade
        slippage_pct: fraction of price applied as slippage (0.001 = 0.1%)
        """
        self.trades = trades.copy()
        self.commission = commission_per_trade
        self.slippage_pct = slippage_pct
        self._compute_returns()

    def _compute_returns(self):
        """Compute PnL and R-multiple for each trade"""
        # Apply slippage
        self.trades['slippage'] = self.trades['entry_price'] * self.slippage_pct
        self.trades['pnl'] = self.trades['direction'] * (self.trades['exit_price'] - self.trades['entry_price'] - self.trades['slippage']) * self.trades['size']
        # Subtract commission
        self.trades['pnl'] -= self.commission

        # Compute cumulative equity
        self.trades['equity_curve'] = self.trades['pnl'].cumsum()

        # Compute drawdown in %
        equity = self.trades['equity_curve']
        peak = equity.cummax()
        self.trades['drawdown_pct'] = (peak - equity) / peak * 100

        # Compute R-multiple assuming 1% risk per trade for simplicity
        risk_per_trade = self.trades['entry_price'] * 0.01
        self.trades['R'] = self.trades['pnl'] / (self.trades['size'] * risk_per_trade)

    def profit_factor(self):
        """Profit Factor = sum(profits) / abs(sum(losses)"""
        profits = self.trades[self.trades['pnl'] > 0]['pnl'].sum()
        losses = self.trades[self.trades['pnl'] < 0]['pnl'].sum()
        return np.inf if losses == 0 else profits / abs(losses)

    def max_drawdown(self):
        """Maximum drawdown in %"""
        return self.trades['drawdown_pct'].max()

    def expectancy(self):
        """Expectancy = average R-multiple"""
        return self.trades['R'].mean()

    def walk_forward_efficiency(self, oos_trades: pd.DataFrame):
        """WFE = PF(OoS) / PF(IS)"""
        in_sample_pf = self.profit_factor()
        oos_audit = PerformanceAudit(oos_trades, self.commission, self.slippage_pct)
        oos_pf = oos_audit.profit_factor()
        return 0 if in_sample_pf == 0 else oos_pf / in_sample_pf

    def plot_equity_curve(self, title="Equity Curve"):
        """Plot equity curve with drawdowns"""
        plt.figure(figsize=(12, 6))
        plt.plot(self.trades['equity_curve'], label='Equity Curve', color='blue')
        plt.fill_between(self.trades.index, self.trades['equity_curve'] - self.trades['drawdown_pct'], self.trades['equity_curve'], color='red', alpha=0.3, label='Drawdown')
        plt.title(title)
        plt.xlabel("Trade #")
        plt.ylabel("Equity")
        plt.legend()
        plt.grid(True)
        plt.show()

    def summary(self):
        """Return key metrics as a dictionary"""
        return {
            "Profit Factor": self.profit_factor(),
            "Max Drawdown %": self.max_drawdown(),
            "Expectancy": self.expectancy()
        }
