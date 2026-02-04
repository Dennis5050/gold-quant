# backend/live/run_live.py

import time
import logging
import pandas as pd

from live.mt5_connector import MT5Connector
from live.heartbeat import Heartbeat
from execution.mt5_executor import MT5Executor
from risk.risk_manager import RiskManager
from risk.kill_switch import KillSwitch
from core.regime_detector import RegimeDetector
from core.feature_engineer import FeatureEngineer
from core.signal_generator import SignalGenerator
from core.validator import Validator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

class LiveTradingSystem:
    def __init__(self, symbols=["XAUUSD"], account_equity=100000):
        self.symbols = symbols

        # Connectors
        self.connector = MT5Connector(mode="paper", symbols=symbols)
        self.executor = MT5Executor(mode="paper")
        self.risk_manager = RiskManager(account_equity=account_equity)
        self.kill_switch = KillSwitch(max_drawdown_pct=0.2, min_expectancy=0.1)
        self.heartbeat = Heartbeat(interval_minutes=15)  # H15 time frame

        # Core
        self.regime_detector = RegimeDetector(vol_window=100)
        self.feature_engineer = FeatureEngineer()
        self.signal_generator = SignalGenerator()
        self.validator = Validator()

        # Initialize
        self.kill_switch.reset(account_equity)

    def run(self):
        logging.info("Starting live trading loop...")
        while True:
            if self.heartbeat.check_time():
                logging.info("Heartbeat triggered. Fetching new data and evaluating trades...")

                for symbol in self.symbols:
                    # Simulated market data fetch
                    df = self._get_market_data(symbol)
                    df = self.feature_engineer.add_features(df)
                    df = self.regime_detector.detect(df)

                    signal = self.signal_generator.generate(df)
                    if not self.validator.validate(signal):
                        logging.info(f"Signal for {symbol} invalid. Skipping trade.")
                        continue

                    # Apply kill switch checks
                    if not self.kill_switch.is_system_active(self.risk_manager.equity, expectancy=0.15):
                        logging.warning("Kill switch triggered. Stopping trading.")
                        return

                    # Calculate position sizing
                    entry_price = df['xau_close'].iloc[-1]
                    atr = df['atr'].iloc[-1]
                    direction = signal['direction']
                    sl, tp = self.risk_manager.apply_sl_tp(entry_price, direction, atr)
                    size = self.risk_manager.calculate_position_size(entry_price, sl)

                    if size > 0:
                        trade = self.executor.send_order(symbol, direction, size, entry_price, sl, tp)
                        logging.info(f"Trade executed: {trade}")

                logging.info("Cycle complete. Waiting for next heartbeat...")
            else:
                # Sleep 1 min to reduce CPU usage
                time.sleep(60)

    def _get_market_data(self, symbol):
        """
        Placeholder: fetch latest H15 OHLCV data
        For now, simulate random prices.
        """
        import numpy as np
        periods = 100
        close = 1900 + np.random.randn(periods).cumsum()
        high = close + np.random.rand(periods)
        low = close - np.random.rand(periods)
        open_ = close - np.random.randn(periods)
        df = pd.DataFrame({
            "open": open_,
            "high": high,
            "low": low,
            "xau_close": close
        })
        return df


if __name__ == "__main__":
    system = LiveTradingSystem(symbols=["XAUUSD", "DXY"], account_equity=100000)
    system.run()
