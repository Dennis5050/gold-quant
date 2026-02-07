# backend/trading/trading_loop.py

import time
import pandas as pd
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

        # Core components
        self.feature_engineer = FeatureEngineer()
        self.regime_detector = RegimeDetector()
        self.signal_generator = SignalGenerator()
        self.validator = Validator()

        # Risk & execution
        self.risk_manager = RiskManager(account_equity=100_000, risk_per_trade=0.01)
        self.kill_switch = KillSwitch(max_drawdown_pct=0.2, min_expectancy=0.1)
        self.executor = MT5Executor(mode=mode)

        # Reset kill switch state
        self.kill_switch.reset(equity=100_000)

        # Ensure MT5 initialized (paper trading can bypass)
        if not mt5.initialize() and self.mode != "paper":
            raise RuntimeError(f"MT5 initialization failed: {mt5.last_error()}")

    def fetch_market_data(self, symbol="XAUUSD", bars=200, timeframe=mt5.TIMEFRAME_M1):
        """
        Fetch OHLC data from MT5. Falls back to dummy data if MT5 fails.
        """
        if self.mode == "paper":
            # Dummy historical data for paper trading
            df = pd.DataFrame({
                "xau_open": [1900 + i for i in range(bars)],
                "xau_high": [1910 + i for i in range(bars)],
                "xau_low": [1890 + i for i in range(bars)],
                "xau_close": [1905 + i for i in range(bars)],
            })
            return df

        # Live MT5 fetch
        try:
            fetcher = MT5DataFetcher(symbol=symbol, timeframe=timeframe, bars=bars)
            df = fetcher.fetch()
            if df is None or df.empty:
                raise ValueError("No data fetched from MT5, using dummy fallback.")
            return df
        except Exception as e:
            print("MT5 fetch failed:", e)
            # fallback
            df = pd.DataFrame({
                "xau_open": [1900 + i for i in range(bars)],
                "xau_high": [1910 + i for i in range(bars)],
                "xau_low": [1890 + i for i in range(bars)],
                "xau_close": [1905 + i for i in range(bars)],
            })
            return df

    def run_once(self, force_test_trade=True):
        # 1️⃣ Fetch market data
        data = self.fetch_market_data()
        if data is None or len(data) < 50:
            print("Not enough data to trade.")
            return

        # 2️⃣ Feature engineering
        data = self.feature_engineer.add_features(data)

        # Ensure key columns exist
        if "xau_close" not in data.columns:
            data["xau_close"] = 1900 + np.arange(len(data))
        if "volatility_10" not in data.columns:
            data["volatility_10"] = data["xau_close"].pct_change().rolling(10).std().fillna(0.001)
        data["volatility_10"] = data["volatility_10"].replace(0, 0.001)

        # 3️⃣ Regime detection
        data = self.regime_detector.detect(data)

        # 4️⃣ Signal generation
        data = self.signal_generator.generate(data)

        # 🚨 Force a test signal if requested
        if force_test_trade:
            print("FORCED TEST SIGNAL TRIGGERED")
            data.loc[data.index[-1], "signal"] = 1

        # 5️⃣ Validation
        data = self.validator.validate(data, state={})

        # 6️⃣ Grab latest row
        latest = data.iloc[-1]
        signal = int(latest.get("signal", 0))
        entry_price = float(latest.get("xau_close", 1900))
        atr = float(latest.get("volatility_10", 5))

        if signal == 0:
            print("No trade signal.")
            return

        # 7️⃣ Kill switch
        if not self.kill_switch.is_system_active(equity=self.risk_manager.account_equity, expectancy=0.5):
            print("Kill switch active – trading halted")
            return

        # 8️⃣ Risk management: SL/TP
        sl, tp, sl_dist, tp_dist = self.risk_manager.apply_sl_tp(entry_price=entry_price, direction=signal, atr=atr)

        # Ensure valid SL/TP values
        if sl is None or np.isnan(sl):
            sl = entry_price - atr if signal > 0 else entry_price + atr
        if tp is None or np.isnan(tp):
            tp = entry_price + 2 * atr if signal > 0 else entry_price - 2 * atr

        # Calculate position size safely
        volume = self.risk_manager.calculate_position_size(entry_price=entry_price, stop_loss_price=sl)
        if volume is None or np.isnan(volume):
            volume = 1  # fallback

        # 9️⃣ Execute trade
        trade = self.executor.send_order(symbol="XAUUSD", direction=signal, volume=volume, price=entry_price, sl=sl, tp=tp)
        print("Trade executed:", trade)

    def run_forever(self, interval_seconds=60):
        print(f"Starting trading loop in {self.mode.upper()} mode...")
        while True:
            try:
                self.run_once(force_test_trade=False)
                time.sleep(interval_seconds)
            except Exception as e:
                print("Trading loop error:", e)
                time.sleep(5)
