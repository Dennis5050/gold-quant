# backend/tests/test_run_all.py

import pandas as pd
from core.regime_detector import RegimeDetector
from core.feature_engineer import FeatureEngineer
from core.signal_generator import SignalGenerator
from core.validator import Validator
from risk.risk_manager import RiskManager
from risk.kill_switch import KillSwitch
from execution.mt5_executor import MT5Executor

# ------------------------------
# 1. Load sample data
# ------------------------------
data_path = "../data/raw/xauusd_h1.csv"  # replace with your actual CSV
try:
    df = pd.read_csv(data_path)
except FileNotFoundError:
    # create dummy data if CSV is missing
    import numpy as np
    df = pd.DataFrame({
        "xau_close": np.random.rand(200) * 2000,
        "dxy_close": np.random.rand(200) * 110
    })

# ------------------------------
# 2. Regime detection
# ------------------------------
regime_detector = RegimeDetector(vol_window=15)
df = regime_detector.detect(df)
print("Regime detection done. Sample regimes:")
print(df[['xau_close', 'vol', 'vol_pct', 'regime']].tail())

# ------------------------------
# 3. Feature engineering
# ------------------------------
feature_engineer = FeatureEngineer()
df = feature_engineer.compute_features(df)
print("Features added:")
print(df.tail())

# ------------------------------
# 4. Signal generation
# ------------------------------
signal_gen = SignalGenerator()
df = signal_gen.generate_signals(df)
print("Signals generated:")
print(df.tail())

# ------------------------------
# 5. Validation
# ------------------------------
validator = Validator()
df = validator.validate_signals(df)
print("Signals validated:")
print(df.tail())

# ------------------------------
# 6. Risk management
# ------------------------------
risk_mgr = RiskManager(account_equity=100000, risk_per_trade=0.01)
stop_loss, take_profit = risk_mgr.apply_sl_tp(entry_price=1950, direction=1, atr=5)
position_size = risk_mgr.calculate_position_size(entry_price=1950, stop_loss_price=stop_loss)
print(f"Position size: {position_size}, SL: {stop_loss}, TP: {take_profit}")

# ------------------------------
# 7. Kill switch
# ------------------------------
kill_switch = KillSwitch(max_drawdown_pct=0.2, min_expectancy=0.1)
kill_switch.reset(equity=100000)
system_ok = kill_switch.is_system_active(equity=95000, expectancy=0.15)
print(f"System active: {system_ok}")

# ------------------------------
# 8. Execution simulation
# ------------------------------
executor = MT5Executor(mode="paper")
trade = executor.send_order(symbol="XAUUSD", direction=1, volume=position_size, price=1950, sl=stop_loss, tp=take_profit)
print("Simulated trade:")
print(trade)

print("\n✅ First-run test completed successfully!")
