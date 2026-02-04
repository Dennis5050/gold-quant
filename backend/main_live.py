# backend/main_live.py

import pandas as pd
import logging
import time
from live.mt5_connector import MT5Connector
from core.regime_detector import RegimeDetector
from core.feature_engineer import FeatureEngineer
from core.signal_generator import SignalGenerator
from risk.risk_manager import RiskManager
from risk.kill_switch import KillSwitch
import os

# ---------------------------
# Setup logging
# ---------------------------
logs_path = "logs"
os.makedirs(logs_path, exist_ok=True)
logging.basicConfig(
    filename=f"{logs_path}/live_trades.log",
    level=logging.INFO,
    format="%(asctime)s,%(message)s"
)
logger = logging.getLogger("LiveTrading")

# ---------------------------
# Initialize modules
# ---------------------------
connector = MT5Connector(mode="live")  # live mode
regime_detector = RegimeDetector(vol_window=100)
feature_engineer = FeatureEngineer()
signal_generator = SignalGenerator()
risk_manager = RiskManager(account_equity=100000, risk_per_trade=0.01)
kill_switch = KillSwitch(max_drawdown_pct=0.2, min_expectancy=0.1)

# Initialize live equity
equity = 100000
kill_switch.reset(equity)

# ---------------------------
# Symbols to trade
# ---------------------------
symbols = ["XAUUSD", "DXY"]

# ---------------------------
# Main live trading loop
# ---------------------------
while True:
    for symbol in symbols:
        # 1. Fetch recent 200 candles (15-min)
        df = connector.get_recent_data(symbol, timeframe="15min", n=200)

        # 2. Compute market regime
        df = regime_detector.detect(df)

        # 3. Feature engineering
        df = feature_engineer.compute_features(df)

        # 4. Generate signals
        signals = signal_generator.generate(df)

        # 5. Latest candle only
        latest_signal = signals.iloc[-1]
        direction = latest_signal['signal']
        price = df['close'].iloc[-1]
        atr = df['atr'].iloc[-1]

        if direction == 0:
            continue  # no trade

        # 6. Calculate stop-loss / take-profit
        sl, tp = risk_manager.apply_sl_tp(price, direction, atr)

        # 7. Calculate position size
        size = risk_manager.calculate_position_size(price, sl)

        # 8. Kill switch check
        if not kill_switch.is_system_active(equity, expectancy=0.2):  # dummy expectancy
            logger.warning(f"{symbol},KILL_SWITCH_TRIGGERED,Equity={equity}")
            continue

        # 9. Send live order
        try:
            trade = connector.send_order(symbol, direction, size, price, sl, tp)
        except Exception as e:
            logger.error(f"Trade failed for {symbol}: {e}")
            continue

        # 10. Update equity (simulate PnL until MT5 confirms)
        pnl = (trade['entry_price'] - price) * direction * size
        equity += pnl

        # 11. Log trade
        logger.info(
            f"{symbol},{direction},{size},{price},{sl},{tp},{equity},{trade['status']}"
        )

    # Wait until the next 15-min candle
    print(f"Waiting for next candle... Current equity: {equity:.2f}")
    time.sleep(15 * 60)  # 15 minutes
