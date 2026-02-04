import pandas as pd
import numpy as np

class RegimeAuditor:
    def __init__(self, regimes=("Range", "Trend", "Chaos")):
        """
        Track performance metrics per regime
        """
        self.regimes = regimes
        # Store trades: {regime: [R-multiples]}
        self.trade_history = {regime: [] for regime in self.regimes}

    def record_trade(self, regime, r_multiple):
        """
        Append a completed trade's R-multiple to the regime history
        """
        if regime not in self.trade_history:
            self.trade_history[regime] = []
        self.trade_history[regime].append(r_multiple)

    def calculate_expectancy(self, regime):
        """
        Expectancy = avg(win) * win_rate - avg(loss) * loss_rate
        R-multiples used to measure each trade
        """
        trades = self.trade_history.get(regime, [])
        if not trades:
            return 0.0  # No trades yet

        wins = [r for r in trades if r > 0]
        losses = [r for r in trades if r < 0]

        win_rate = len(wins) / len(trades) if trades else 0
        avg_win = np.mean(wins) if wins else 0
        avg_loss = np.mean(losses) if losses else 0

        expectancy = (avg_win * win_rate) + (avg_loss * (1 - win_rate))
        return expectancy

    def global_expectancy(self):
        """
        Weighted average expectancy across all regimes
        """
        all_trades = [r for trades in self.trade_history.values() for r in trades]
        if not all_trades:
            return 0.0

        wins = [r for r in all_trades if r > 0]
        losses = [r for r in all_trades if r < 0]

        win_rate = len(wins) / len(all_trades)
        avg_win = np.mean(wins) if wins else 0
        avg_loss = np.mean(losses) if losses else 0

        return (avg_win * win_rate) + (avg_loss * (1 - win_rate))

    def summary(self):
        """
        Returns a DataFrame of expectancy per regime
        """
        data = {regime: self.calculate_expectancy(regime) for regime in self.regimes}
        return pd.DataFrame.from_dict(data, orient='index', columns=['Expectancy'])
