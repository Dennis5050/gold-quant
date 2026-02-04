# backend/run.py

import os
import logging
import pandas as pd
from datetime import datetime

# Core modules
from core.feature_engineer import FeatureEngineer
from core.regime_detector import RegimeDetector
from core.signal_generator import SignalGenerator
from core.validator import Validator

# Risk modules
from risk.risk_manager import RiskManager
from risk.kill_switch import KillSwitch

# Execution modules
from execution.mt5_executor import MT5Executor

# Logging setup
log_file = os.path.join("logs", "system.log")
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("GoldQuant")

def run_backtest(df):
    """Run a historical backtest"""
    logger.info("Starting backtest...")
    fe = FeatureEngineer()
    rd = RegimeDetector()
    sg = SignalGenerator()
    val = Validator()
    rm = RiskManager()
    
    df = fe.engineer_features(df)
    df = rd.detect(df)

    trades = []
    for i, row in df.iterrows():
        signals = sg.generate_signal(row)
        if val.validate(signals):
            size = rm.calculate_position_size(
                entry_price=row["xau_close"], 
                stop_loss_price=row["xau_close"]*0.99  # example SL
            )
            trade = {
                "timestamp": row.name,
                "signal": signals,
                "size": size,
                "price": row["xau_close"]
            }
            trades.append(trade)
            logger.info(f"Backtest trade: {trade}")
    return pd.DataFrame(trades)

def run_paper(df):
    """Run shadow trading in paper mode"""
    logger.info("Starting paper trading...")
    fe = FeatureEngineer()
    rd = RegimeDetector()
    sg = SignalGenerator()
    val = Validator()
    rm = RiskManager()
    ks = KillSwitch()
    ks.reset(rm.equity)
    executor = MT5Executor(mode="paper")

    df = fe.engineer_features(df)
    df = rd.detect(df)

    for i, row in df.iterrows():
        signals = sg.generate_signal(row)
        if val.validate(signals) and ks.is_system_active(rm.equity, 0.2):
            size = rm.calculate_position_size(
                entry_price=row["xau_close"],
                stop_loss_price=row["xau_close"]*0.99
            )
            trade = executor.send_order(
                symbol="XAUUSD",
                direction=signals.get("direction", 0),
                volume=size,
                price=row["xau_close"]
            )
            logger.info(f"Paper trade executed: {trade}")

def run_live():
    """Run live trading (requires MT5 setup)"""
    logger.info("Starting live trading...")
    executor = MT5Executor(mode="live")
    # Placeholder: real-time streaming loop here
    logger.warning("Live trading loop not implemented yet!")

if __name__ == "__main__":
    mode = input("Select mode (backtest/paper/live): ").strip().lower()

    # Example: load historical 15-min data
    data_file = os.path.join("data", "raw", "xauusd_h1.csv")
    if os.path.exists(data_file):
        df = pd.read_csv(data_file, index_col=0, parse_dates=True)
    else:
        df = pd.DataFrame()  # empty fallback

    if mode == "backtest":
        trades_df = run_backtest(df)
        trades_df.to_csv(os.path.join("logs", "backtest_trades.csv"))
        logger.info("Backtest completed.")
    elif mode == "paper":
        run_paper(df)
        logger.info("Paper trading completed.")
    elif mode == "live":
        run_live()
    else:
        logger.error(f"Unknown mode: {mode}")
        print("Invalid mode selected. Choose backtest, paper, or live.")
