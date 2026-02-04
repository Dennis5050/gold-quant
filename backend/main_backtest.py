# backend/main_backtest.py

import pandas as pd
import os
from backtest.backtester import Backtester
from backtest.performance_audit import PerformanceAudit
from core.regime_detector import RegimeDetector
from core.feature_engineer import FeatureEngineer
from core.signal_generator import SignalGenerator
from risk.risk_manager import RiskManager
from risk.kill_switch import KillSwitch

# ---------------------------
# Config
# ---------------------------
SYMBOLS = ["XAUUSD", "DXY"]
TIMEFRAME = "15min"
HISTORICAL_CANDLES = 1000

ACCOUNT_EQUITY = 100000
RISK_PER_TRADE = 0.01
MAX_DRAWDOWN = 0.2
MIN_EXPECTANCY = 0.1

# ---------------------------
# Initialize modules
# ---------------------------
regime_detector = RegimeDetector(vol_window=100)
feature_engineer = FeatureEngineer()
signal_generator = SignalGenerator()
risk_manager = RiskManager(account_equity=ACCOUNT_EQUITY, risk_per_trade=RISK_PER_TRADE)
kill_switch = KillSwitch(max_drawdown_pct=MAX_DRAWDOWN, min_expectancy=MIN_EXPECTANCY)

# ---------------------------
# Backtest each symbol
# ---------------------------
for symbol in SYMBOLS:
    # Load historical data
    df = pd.read_csv(f"data/raw/{symbol.lower()}_h1.csv")
    
    # Use only last N candles
    df = df.tail(HISTORICAL_CANDLES).copy()

    # Detect regime
    df = regime_detector.detect(df)

    # Compute features
    df = feature_engineer.compute_features(df)

    # Generate signals
    df_signals = signal_generator.generate(df)

    # Initialize Backtester
    bt = Backtester(
        df=df_signals,
        risk_manager=risk_manager,
        kill_switch=kill_switch,
        symbol=symbol
    )

    # Run backtest
    equity_curve = bt.run()

    # Performance Audit
    audit = PerformanceAudit(equity_curve)
    audit.report()

    # Optional: save results
    os.makedirs("data/processed", exist_ok=True)
    equity_curve.to_csv(f"data/processed/{symbol.lower()}_equity_curve.csv", index=False)
    print(f"Backtest complete for {symbol}. Equity curve saved.")
