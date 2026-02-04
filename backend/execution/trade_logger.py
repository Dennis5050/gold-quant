# backend/execution/trade_logger.py

import csv
import os
import logging
from datetime import datetime

# Ensure logs folder exists
LOGS_FOLDER = os.path.join(os.path.dirname(__file__), "../logs")
os.makedirs(LOGS_FOLDER, exist_ok=True)

TRADES_FILE = os.path.join(LOGS_FOLDER, "trades.csv")
REJECTED_FILE = os.path.join(LOGS_FOLDER, "rejected_trades.csv")
SYSTEM_LOG = os.path.join(LOGS_FOLDER, "system.log")


# Configure Python logger for system messages
logging.basicConfig(
    filename=SYSTEM_LOG,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


class TradeLogger:
    """Handles trade logging for executed and rejected trades"""

    @staticmethod
    def log_trade(trade):
        """Append executed trade to trades.csv"""
        fieldnames = ["timestamp", "symbol", "direction", "size", "entry", "sl", "tp", "status"]
        file_exists = os.path.exists(TRADES_FILE)

        with open(TRADES_FILE, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow({
                "timestamp": datetime.now().isoformat(),
                "symbol": trade.get("symbol"),
                "direction": trade.get("direction"),
                "size": trade.get("size"),
                "entry": trade.get("entry"),
                "sl": trade.get("sl"),
                "tp": trade.get("tp"),
                "status": trade.get("status", "executed"),
            })

    @staticmethod
    def log_rejected(trade, reason=""):
        """Append rejected trade to rejected_trades.csv"""
        fieldnames = ["timestamp", "symbol", "direction", "size", "entry", "reason"]
        file_exists = os.path.exists(REJECTED_FILE)

        with open(REJECTED_FILE, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow({
                "timestamp": datetime.now().isoformat(),
                "symbol": trade.get("symbol"),
                "direction": trade.get("direction"),
                "size": trade.get("size"),
                "entry": trade.get("entry"),
                "reason": reason,
            })

    @staticmethod
    def log_system(message, level="info"):
        """Log general system messages"""
        if level == "warning":
            logging.warning(message)
        elif level == "error":
            logging.error(message)
        else:
            logging.info(message)
