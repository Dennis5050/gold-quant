import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime

class MT5DataFetcher:
    def __init__(self, symbol="XAUUSD", timeframe=mt5.TIMEFRAME_M1, bars=200):
        self.symbol = symbol
        self.timeframe = timeframe
        self.bars = bars

        if not mt5.initialize():
            raise RuntimeError("MT5 initialization failed")

    def fetch(self):
        rates = mt5.copy_rates_from_pos(
            self.symbol,
            self.timeframe,
            0,
            self.bars
        )

        if rates is None or len(rates) == 0:
            return None

        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s")

        # 🔒 STANDARDIZED PRICE COLUMNS
        return df[["time", "open", "high", "low", "close", "tick_volume"]]
