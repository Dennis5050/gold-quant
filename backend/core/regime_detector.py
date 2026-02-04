# backend/core/regime_detector.py

import numpy as np
import pandas as pd

class RegimeDetector:
    def __init__(self, vol_window=20, sma_window=10):
        self.vol_window = vol_window
        self.sma_window = sma_window

    def detect(self, df):
        """
        Detect market regime:
        0 = Range
        1 = Trend
        2 = Chaos
        Adds 'bias' for trend direction (1=long, -1=short)
        """
        # Ensure required columns exist
        required_cols = ['xau_open', 'xau_high', 'xau_low', 'xau_close']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing column '{col}' in input data")

        # 1. Volatility
        df['returns'] = df['xau_close'].pct_change()
        df['vol'] = df['returns'].rolling(self.vol_window).std()
        df['vol_pct'] = df['vol'].rank(pct=True)

        # 2. SMA slope as trend proxy
        df['sma_slope'] = df['xau_close'].rolling(self.sma_window).mean().diff()

        # 3. Determine regime
        df['regime'] = 0  # Default = Range
        df.loc[df['vol_pct'] > 0.9, 'regime'] = 2  # Chaos
        df.loc[df['sma_slope'].abs() > 0.1, 'regime'] = 1  # Trend (example threshold)

        # 4. Add bias for trend rows
        mask = df['regime'] == 1
        df.loc[mask, 'bias'] = np.where(df.loc[mask, 'sma_slope'] > 0, 1, -1)

        # Fill NaN bias for non-trend rows
        df['bias'].fillna(0, inplace=True)

        return df
