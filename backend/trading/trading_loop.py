# backend/trading/trading_loop.py

import time
import numpy as np
import MetaTrader5 as mt5

from backend.data.mt5_data import MT5DataFetcher
from backend.core.regime_detector import RegimeDetector
from backend.core.feature_engineer import FeatureEngineer
from backend.core.signal_generator import SignalGenerator
from backend.core.validator import Validator
from backend.risk.risk_manager import RiskManager
from backend.risk.kill_switch import KillSwitch
from backend.execution.mt5_executor import MT5Executor


class TradingLoop:
    def __init__(self, mode="paper"):
        self.mode = mode

        # Core
        self.feature_engineer = FeatureEngineer()
        self.regime_detector = RegimeDetector()
        self.signal_generator = SignalGenerator()
        self.validator = Validator()

        # Risk & execution
        self.risk_manager = RiskManager(account_equity=100_000, risk_per_trade=0.01)
        self.kill_switch = KillSwitch(max_drawdown_pct=0.2, min_expectancy=0.1)
        self.executor = MT5Executor(mode=mode)

        self.kill_switch.reset(equity=100_000)

    # =========================
    # Market data (MT5)
    # =========================
    def fetch_market_data(self):
        fetcher = MT5DataFetcher(
            symbol="XAUUSD",
            timeframe=mt5.TIMEFRAME_M1,
            bars=200
        )
        return fetcher.fetch()

    # =========================
    # Single iteration
    # =========================
    def run_once(self, force_test_trade=False):
        # 1️⃣ Fetch data
        data = self.fetch_market_data()
        if data is None or len(data) < 50:
            print("Not enough data.")
            return

        # 2️⃣ Features
        data = self.feature_engineer.add_features(data)

        # Ensure volatility exists
        if "volatility_10" not in data.columns:
            data["volatility_10"] = (
                data["xau_close"]
                .pct_change()
                .rolling(10)
                .std()
                .fillna(0.001)
            )
        data["volatility_10"] = data["volatility_10"].replace(0, 0.001)

        # 3️⃣ Regime
        data = self.regime_detector.detect(data)

        # 4️⃣ Signal
        data = self.signal_generator.generate(data)

        if force_test_trade:
            print("FORCED TEST SIGNAL TRIGGERED")
            data.loc[data.index[-1], "signal"] = 1

        # 5️⃣ Validation
        data = self.validator.validate(data, state={})

        latest = data.iloc[-1]
        signal = int(latest.get("signal", 0))

        if signal == 0:
            print("No trade signal.")
            return

        entry_price = float(latest["xau_close"])
        atr = float(latest["volatility_10"])

        # 6️⃣ Kill switch
        if not self.kill_switch.is_system_active(
            equity=self.risk_manager.account_equity,
            expectancy=0.5
        ):
            print("Kill switch active – halted.")
            return

        # 7️⃣ Risk
        sl, tp, *_ = self.risk_manager.apply_sl_tp(
            entry_price=entry_price,
            direction=signal,
            atr=atr
        )

        volume = self.risk_manager.calculate_position_size(
            entry_price=entry_price,
            stop_loss_price=sl
        )

        if volume is None or np.isnan(volume):
            volume = 1

        # 8️⃣ Execute
        trade = self.executor.send_order(
            symbol="XAUUSD",
            direction=signal,
            volume=volume,
            price=entry_price,
            sl=sl,
            tp=tp
        )

        print("Trade executed:", trade)

    # =========================
    # Continuous loop
    # =========================
    def run_forever(self, interval_seconds=60):
        print(f"Trading started ({self.mode.upper()})")
        while True:
            try:
                self.run_once(force_test_trade=False)
                time.sleep(interval_seconds)
            except Exception as e:
                print("Loop error:", e)
                time.sleep(5)
