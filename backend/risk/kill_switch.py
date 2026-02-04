class KillSwitch:
    def __init__(self, max_drawdown_pct=0.2, min_expectancy=0.1):
        """
        max_drawdown_pct: max loss allowed relative to starting equity (e.g., 0.2 = 20%)
        min_expectancy: minimum R-multiple expectancy allowed to keep trading
        """
        self.max_drawdown_pct = max_drawdown_pct
        self.min_expectancy = min_expectancy
        self.start_equity = None

    def reset(self, equity):
        """Initialize starting equity for tracking drawdown"""
        self.start_equity = equity

    def check_equity(self, equity):
        """Returns True if equity is above drawdown limit"""
        if self.start_equity is None:
            self.start_equity = equity
        drawdown = (self.start_equity - equity) / self.start_equity
        return drawdown < self.max_drawdown_pct

    def check_expectancy(self, expectancy):
        """Returns True if expectancy is above minimum threshold"""
        return expectancy >= self.min_expectancy

    def is_system_active(self, equity, expectancy):
        """
        Combine checks for equity and expectancy
        Returns True if system can trade, False if kill switch triggered
        """
        equity_ok = self.check_equity(equity)
        expectancy_ok = self.check_expectancy(expectancy)
        return equity_ok and expectancy_ok
