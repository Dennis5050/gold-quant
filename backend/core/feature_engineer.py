import pandas as pd
import numpy as np


class FeatureEngineer:
    def __init__(self, z_window=20):
        self.z_window = z_window

    def add_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Returns
        df["returns"] = df["xau_close"].pct_change().fillna(0)

        # Moving averages
        df["sma_5"] = df["xau_close"].rolling(5).mean()
        df["sma_10"] = df["xau_close"].rolling(10).mean()
        df["sma_diff"] = (df["sma_5"] - df["sma_10"]).fillna(0)

        # Volatility
        df["volatility_5"] = df["returns"].rolling(5).std().fillna(0)
        df["volatility_10"] = df["returns"].rolling(10).std().fillna(0)

        # Momentum
        df["mom"] = df["xau_close"].diff().fillna(0)

        # 🔑 Z-SCORE (THIS FIXES YOUR ERROR)
        rolling_mean = df["xau_close"].rolling(self.z_window).mean()
        rolling_std = df["xau_close"].rolling(self.z_window).std()

        df["zscore"] = ((df["xau_close"] - rolling_mean) / rolling_std).fillna(0)

        return df
