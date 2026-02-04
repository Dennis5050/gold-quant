# backend/backtest/walk_forward.py

import pandas as pd
from backtest.backtester import Backtester
from backtest.performance_audit import PerformanceAudit
import matplotlib.pyplot as plt

class WalkForward:
    """
    Walk-forward validation engine.
    Splits data into rolling in-sample (IS) and out-of-sample (OOS) periods,
    backtests each IS period, evaluates OOS performance, and computes WFE.
    """

    def __init__(self, data: pd.DataFrame, strategy_class, is_window=1000, oos_window=250, **strategy_kwargs):
        """
        data: DataFrame with market data (OHLC)
        strategy_class: class implementing the strategy (e.g., Backtester)
        is_window: number of candles for in-sample
        oos_window: number of candles for out-of-sample
        strategy_kwargs: arguments passed to strategy_class
        """
        self.data = data
        self.strategy_class = strategy_class
        self.is_window = is_window
        self.oos_window = oos_window
        self.strategy_kwargs = strategy_kwargs
        self.results = []

    def run(self):
        start = 0
        total_length = len(self.data)

        while start + self.is_window + self.oos_window <= total_length:
            is_data = self.data.iloc[start:start+self.is_window]
            oos_data = self.data.iloc[start+self.is_window:start+self.is_window+self.oos_window]

            # Backtest in-sample
            is_bt = self.strategy_class(is_data, **self.strategy_kwargs)
            is_trades = is_bt.run_backtest()
            is_audit = PerformanceAudit(is_trades)
            
            # Backtest out-of-sample using same strategy parameters
            oos_bt = self.strategy_class(oos_data, **self.strategy_kwargs)
            oos_trades = oos_bt.run_backtest()
            oos_audit = PerformanceAudit(oos_trades)

            # Compute WFE
            wfe = 0 if is_audit.profit_factor() == 0 else oos_audit.profit_factor() / is_audit.profit_factor()

            # Store results
            self.results.append({
                "IS_start": is_data.index[0],
                "IS_end": is_data.index[-1],
                "OOS_start": oos_data.index[0],
                "OOS_end": oos_data.index[-1],
                "IS_PF": is_audit.profit_factor(),
                "OOS_PF": oos_audit.profit_factor(),
                "IS_MaxDD%": is_audit.max_drawdown(),
                "OOS_MaxDD%": oos_audit.max_drawdown(),
                "IS_Expectancy": is_audit.expectancy(),
                "OOS_Expectancy": oos_audit.expectancy(),
                "WFE": wfe,
                "IS_trades": is_trades,
                "OOS_trades": oos_trades
            })

            start += self.oos_window  # roll forward

        return pd.DataFrame(self.results)

    def plot_all_equity_curves(self):
        """Plot equity curves for all OOS periods"""
        plt.figure(figsize=(14, 7))
        for i, res in enumerate(self.results):
            equity_curve = res['OOS_trades']['equity_curve']
            plt.plot(equity_curve.index, equity_curve.values, label=f"OOS {i+1}")
        plt.title("Walk-Forward Out-of-Sample Equity Curves")
        plt.xlabel("Trade #")
        plt.ylabel("Equity")
        plt.legend()
        plt.grid(True)
        plt.show()

    def summary(self):
        """Aggregate metrics across all periods"""
        df = pd.DataFrame(self.results)
        summary = {
            "Avg_IS_PF": df['IS_PF'].mean(),
            "Avg_OOS_PF": df['OOS_PF'].mean(),
            "Avg_WFE": df['WFE'].mean(),
            "Avg_IS_MaxDD%": df['IS_MaxDD%'].mean(),
            "Avg_OOS_MaxDD%": df['OOS_MaxDD%'].mean(),
            "Avg_IS_Expectancy": df['IS_Expectancy'].mean(),
            "Avg_OOS_Expectancy": df['OOS_Expectancy'].mean()
        }
        return summary
