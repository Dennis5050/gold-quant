# backend/risk/kill_switch.py
class KillSwitch:
    def __init__(self, max_drawdown_pct=0.2, min_expectancy=0.1):
        """
        max_drawdown_pct: max loss allowed relative to starting equity (e.g., 0.2 = 20%)
        min_expectancy: minimum R-multiple expectancy allowed to keep trading
        """
        self.max_drawdown_pct = max_drawdown_pct
        self.min_expectancy = min_expectancy
        self.start_equity = None
        self.max_equity = None
        self.triggered = False

    def reset(self, equity):
        """Initialize starting equity for tracking drawdown"""
        self.start_equity = equity
        self.max_equity = equity
        self.triggered = False

    def check_equity(self, equity):
        """Check equity drawdown"""
        if self.start_equity is None:
            self.reset(equity)

        # Update max equity seen
        self.max_equity = max(self.max_equity, equity)

        # Calculate drawdown from max equity
        drawdown = (self.max_equity - equity) / self.max_equity
        if drawdown >= self.max_drawdown_pct:
            self.triggered = True
            print(f"[KILL SWITCH] Max drawdown exceeded: {drawdown:.2%}")
            return False
        return True

    def check_expectancy(self, expectancy):
        """Check expectancy threshold"""
        if expectancy < self.min_expectancy:
            self.triggered = True
            print(f"[KILL SWITCH] Expectancy too low: {expectancy:.2f}")
            return False
        return True

    def is_system_active(self, equity, expectancy):
        """
        Combine equity and expectancy checks.
        Returns True if system can trade, False if kill switch triggered.
        """
        if self.triggered:
            return False

        equity_ok = self.check_equity(equity)
        expectancy_ok = self.check_expectancy(expectancy)
        return equity_ok and expectancy_ok
