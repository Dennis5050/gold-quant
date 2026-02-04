# backend/live/run_live.py

import pandas as pd
import logging
import time
import os
from live.mt5_connector import MT5Connector
from core.regime_detector import RegimeDetector
from core.feature_engineer import FeatureEngineer
from core.signal_generator import SignalGenerator
from risk.risk_manager import RiskManager
from risk.kill_switch import KillSwitch

# ---------------------------
# Config
# ---------------------------
MODE = "paper"  # "paper" or "live"
SYMBOLS = ["XAUUSD", "DXY"]
TIMEFRAME = "15min"
CANDLES = 200

ACCOUNT_EQUITY = 100000
RISK_PER_TRADE = 0.01
MAX_DRAWDOWN = 0.2
MIN_EXPECTANCY = 0.1

# ---------------------------
# Setup logging
# ---------------------------
logs_path = "logs"
os.makedirs(logs_path, exist_ok=True)
logging.basicConfig(
    filename=f"{logs_path}/run_live.log",
    level=logging.INFO,
    format="%(asctime)s,%(message)s"
)
logger = logging.getLogger("RunLive")

# ---------------------------
# Initialize modules
# ---------------------------
connector = MT5Connector(mode=MODE)
regime_detector = RegimeDetector(vol_window=100)
feature_engineer = FeatureEngineer()
signal_generator = SignalGenerator()
risk_manager = RiskManager(account_equity=ACCOUNT_EQUITY, risk_per_trade=RISK_PER_TRADE)
kill_switch = KillSwitch(max_drawdown_pct=MAX_DRAWDOWN, min_expectancy=MIN_EXPECTANCY)

equity = ACCOUNT_EQUITY
kill_switch.reset(equity)

# ---------------------------
# Main live/paper trading loop
# ---------------------------
while True:
    for symbol in SYMBOLS:
        # Fetch recent candles
        df = connector.get_recent_data(symbol, timeframe=TIMEFRAME, n=CANDLES)

        # Detect market regime
        df = regime_detector.detect(df)

        # Compute features
        df = feature_engineer.compute_features(df)

        # Generate signals
        signals = signal_generator.generate(df)

        # Latest candle only
        latest_signal = signals.iloc[-1]
        direction = latest_signal['signal']
        price = df['close'].iloc[-1]
        atr = df['atr'].iloc[-1]

        if direction == 0:
            continue  # no trade

        # Stop-loss / take-profit
        sl, tp = risk_manager.apply_sl_tp(price, direction, atr)

        # Position size
        size = risk_manager.calculate_position_size(price, sl)

        # Kill switch check
        if not kill_switch.is_system_active(equity, expectancy=0.2):  # dummy expectancy
            logger.warning(f"{symbol},KILL_SWITCH_TRIGGERED,Equity={equity}")
            continue

        # Send order
        try:
            trade = connector.send_order(symbol, direction, size, price, sl, tp)
        except Exception as e:
            logger.error(f"Trade failed for {symbol}: {e}")
            continue

        # Update equity (simulate PnL in paper mode)
        if MODE == "paper":
            pnl = (trade['entry_price'] - price) * direction * size
            equity += pnl

        # Log trade
        logger.info(
            f"{symbol},{direction},{size},{price},{sl},{tp},{equity},{trade['status']}"
        )

    print(f"[{MODE.upper()} MODE] Waiting for next candle... Current equity: {equity:.2f}")
    time.sleep(15 * 60)  # 15 minutes
