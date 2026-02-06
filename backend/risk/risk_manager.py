# backend/risk/risk_manager.py

class RiskManager:
    """
    Handles risk management: position sizing, stop loss (SL), take profit (TP),
    and ensures trades conform to account equity and risk settings.
    """

    def __init__(self, account_equity=100_000, risk_per_trade=0.01):
        """
        Initialize the RiskManager.
        :param account_equity: Total capital available for trading
        :param risk_per_trade: Fraction of equity to risk per trade (0 < risk_per_trade < 1)
        """
        self.account_equity = account_equity
        self.risk_per_trade = risk_per_trade

    def calculate_position_size(self, entry_price, stop_loss_price):
        """
        Calculate trade volume based on risk per trade and stop loss distance.
        :param entry_price: Price at which the trade is entered
        :param stop_loss_price: Stop loss price
        :return: Position size (units)
        """
        if stop_loss_price == entry_price:
            # Avoid division by zero
            print("Warning: Stop loss equals entry price. Defaulting volume=1")
            return 1

        risk_amount = self.account_equity * self.risk_per_trade
        sl_distance = abs(entry_price - stop_loss_price)
        position_size = risk_amount / sl_distance

        return max(position_size, 1)  # Minimum 1 unit

    def apply_sl_tp(self, entry_price, direction, atr=5):
        """
        Return SL, TP, and distances for a trade.
        :param entry_price: Trade entry price
        :param direction: 1 = long/buy, -1 = short/sell
        :param atr: Average True Range fallback for SL/TP
        :return: sl, tp, sl_distance, tp_distance
        """
        if direction not in [1, -1]:
            raise ValueError("Direction must be 1 (buy) or -1 (sell)")

        sl_distance = atr
        tp_distance = atr * 2  # 2:1 reward:risk ratio

        if direction == 1:
            sl = entry_price - sl_distance
            tp = entry_price + tp_distance
        else:
            sl = entry_price + sl_distance
            tp = entry_price - tp_distance

        return sl, tp, sl_distance, tp_distance

    def update_equity(self, pnl):
        """
        Update account equity based on PnL from closed trades.
        :param pnl: Profit or loss from a trade
        """
        self.account_equity += pnl
        print(f"Account equity updated: {self.account_equity:.2f}")
