# backend/risk/risk_manager.py

class RiskManager:
    def __init__(self, account_equity=100000, risk_per_trade=0.01):
        """
        account_equity: total account balance
        risk_per_trade: fraction of account to risk per trade (e.g., 0.01 = 1%)
        """
        self.equity = account_equity
        self.risk_per_trade = risk_per_trade

    def calculate_position_size(self, entry_price, stop_loss_price, contract_size=1):
        """
        Returns the trade size (units/contracts) based on risk and stop-loss distance.
        """
        # 1. Calculate risk in price units
        risk_price = abs(entry_price - stop_loss_price)
        if risk_price == 0:
            return 0  # avoid division by zero

        # 2. Dollar risk per trade
        dollar_risk = self.equity * self.risk_per_trade

        # 3. Position size
        size = (dollar_risk / risk_price) * contract_size
        size = max(size, 0)  # enforce non-negative
        size = round(size, 2)  # round to 2 decimals for broker compatibility
        return size

    def apply_sl_tp(self, entry_price, direction, atr, sl_multiplier=1.5, tp_multiplier=3):
        """
        Calculate SL and TP using ATR multiples.
        direction: 1 = LONG, -1 = SHORT
        atr: Average True Range
        Returns:
            stop_loss, take_profit, sl_distance, tp_distance
        """
        if direction == 1:  # LONG
            stop_loss = entry_price - atr * sl_multiplier
            take_profit = entry_price + atr * tp_multiplier
        elif direction == -1:  # SHORT
            stop_loss = entry_price + atr * sl_multiplier
            take_profit = entry_price - atr * tp_multiplier
        else:
            stop_loss, take_profit = entry_price, entry_price  # no trade

        # Rounding for broker
        stop_loss = round(stop_loss, 2)
        take_profit = round(take_profit, 2)

        sl_distance = abs(entry_price - stop_loss)
        tp_distance = abs(take_profit - entry_price)

        return stop_loss, take_profit, sl_distance, tp_distance
