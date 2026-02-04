# backend/tests/test_run_all.py

"""
Run all basic tests for gold-quant backend.
"""

import pandas as pd
import numpy as np

from backend.core.regime_detector import RegimeDetector
from backend.core.feature_engineer import FeatureEngineer
from backend.core.signal_generator import SignalGenerator
from backend.core.validator import Validator
from backend.risk.risk_manager import RiskManager
from backend.risk.kill_switch import KillSwitch
from backend.execution.mt5_executor import MT5Executor


def test_regime_detector():
    print("Testing RegimeDetector...")
    data = pd.DataFrame({
        "xau_open": np.random.random(200) * 2000,
        "xau_high": np.random.random(200) * 2000,
        "xau_low": np.random.random(200) * 2000,
        "xau_close": np.random.random(200) * 2000
    })
    detector = RegimeDetector(vol_window=20)
    result = detector.detect(data)
    # Make a copy to avoid chained assignment warning
    result = result.copy()
    print(result[['xau_close', 'vol', 'vol_pct', 'sma_slope', 'regime', 'bias']].tail())


def test_feature_engineer():
    print("Testing FeatureEngineer...")
    data = pd.DataFrame({
        "xau_close": np.random.random(200) * 2000
    })
    fe = FeatureEngineer()
    result = fe.add_features(data)
    print(result.head())


def test_signal_generator():
    print("Testing SignalGenerator...")
    # Include columns required by SignalGenerator
    data = pd.DataFrame({
        "zscore": np.random.randn(200),
        "mom": np.random.randn(200),
        "vol_pct": np.random.random(200),
        "regime": np.random.choice([0, 1, 2], size=200)
    })
    sg = SignalGenerator()
    signals = sg.generate(data)  # using the updated .generate() method
    print(signals.tail())
def test_validator():
    print("Testing Validator...")
    # Include regime column for validation
    data = pd.DataFrame({
        "xau_close": np.random.random(200) * 2000,
        "signal": np.random.choice([-1, 0, 1], size=200),
        "regime": np.random.choice([0, 1, 2], size=200)  # added regime
    })
    v = Validator()
    validated = v.validate(data.copy(), state={})
    print(validated.tail())

def test_risk_manager():
    print("Testing RiskManager...")
    rm = RiskManager(account_equity=100000, risk_per_trade=0.01)
    size = rm.calculate_position_size(entry_price=1900, stop_loss_price=1890)
    # Unpack all four values returned by apply_sl_tp
    sl, tp, sl_dist, tp_dist = rm.apply_sl_tp(entry_price=1900, direction=1, atr=5)
    print(f"Position size: {size}, SL: {sl}, TP: {tp}, SL_dist: {sl_dist}, TP_dist: {tp_dist}")


def test_kill_switch():
    print("Testing KillSwitch...")
    ks = KillSwitch(max_drawdown_pct=0.2, min_expectancy=0.1)
    ks.reset(equity=100000)
    active = ks.is_system_active(equity=95000, expectancy=0.15)
    print(f"System active: {active}")


def test_mt5_executor():
    print("Testing MT5Executor (paper mode)...")
    mt5 = MT5Executor(mode="paper")
    trade = mt5.send_order(symbol="XAUUSD", direction=1, volume=1, price=1900, sl=1890, tp=1920)
    print(trade)


if __name__ == "__main__":
    test_regime_detector()
    test_feature_engineer()
    test_signal_generator()
    test_validator()
    test_risk_manager()
    test_kill_switch()
    test_mt5_executor()
    print("All backend tests completed successfully!")
