import pandas as pd
import numpy as np
from core.regime_detector import RegimeDetector
from core.feature_engineer import FeatureEngineer
from core.signal_generator import SignalGenerator
from core.validator import Validator
from execution.virtual_broker import VirtualBroker

# -----------------------------
# CONFIG
# -----------------------------
INITIAL_EQUITY = 100_000
VOL_WINDOW = 96  # ~1 day of M15 candles
MAX_VOL_PCT = 0.95
RISK_PER_TRADE = 0.01  # 1% equity

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv('data/raw/xauusd_m15.csv', parse_dates=['datetime'])
df = df.sort_values('datetime').reset_index(drop=True)

# -----------------------------
# INIT SYSTEM MODULES
# -----------------------------
regime_detector = RegimeDetector(vol_window=VOL_WINDOW)
feature_engineer = FeatureEngineer()
signal_generator = SignalGenerator()
validator = Validator(max_vol_pct=MAX_VOL_PCT)
broker = VirtualBroker(initial_equity=INITIAL_EQUITY)

# System state
state = {
    "is_active": True,
    "open_pos": False,
    "equity": INITIAL_EQUITY
}

# -----------------------------
# RUN BACKTEST LOOP
# -----------------------------
for idx in range(VOL_WINDOW, len(df)):
    slice_df = df.iloc[:idx+1]  # Use all historical up to current candle
    
    # --- 1. Regime Detection ---
    slice_df = regime_detector.detect(slice_df)
    current_regime = slice_df.iloc[-1]['regime']
    
    # --- 2. Feature Engineering ---
    slice_df = feature_engineer.apply(slice_df)
    
    # --- 3. Signal Generation ---
    signal = signal_generator.generate(slice_df)
    
    # --- 4. Prepare signal row for validation ---
    signal_row = slice_df.iloc[-1].copy()
    signal_row['signal'] = signal
    signal_row['regime'] = current_regime
    
    # --- 5. Validate Signal ---
    is_valid = validator.validate(signal_row, state)
    
    # --- 6. Execute Virtual Trade ---
    if is_valid:
        trade_result = broker.execute(signal, slice_df.iloc[-1], risk_pct=RISK_PER_TRADE)
        state['open_pos'] = False  # Reset after trade (simplified)
        state['equity'] = broker.equity
        status = f"TRADE EXECUTED: {trade_result}"
    else:
        status = "NO TRADE"

    # --- 7. Log System State ---
    print(f"[{slice_df.iloc[-1]['datetime']}] | REGIME: {current_regime} | SIGNAL: {signal} | EQUITY: {state['equity']:.2f} | STATUS: {status}")

# -----------------------------
# PERFORMANCE SUMMARY
# -----------------------------
print("\n--- BACKTEST COMPLETE ---")
print(f"Final Equity: {broker.equity:.2f}")
print(f"Total Trades: {len(broker.trade_history)}")
