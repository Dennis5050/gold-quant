import numpy as np
import pandas as pd

class RegimeDetector:
    def __init__(self, vol_window=100, trend_window=50, atr_window=14):
        """
        vol_window   : lookback for volatility percentile (M15)
        trend_window : lookback for simple slope-based trend
        atr_window   : lookback for ATR (volatility magnitude)
        """
        self.vol_window = vol_window
        self.trend_window = trend_window
        self.atr_window = atr_window

    def calculate_atr(self, df):
        """Average True Range"""
        df['high_low'] = df['xau_high'] - df['xau_low']
        df['high_close'] = np.abs(df['xau_high'] - df['xau_close'].shift())
        df['low_close'] = np.abs(df['xau_low'] - df['xau_close'].shift())
        df['tr'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
        df['atr'] = df['tr'].rolling(self.atr_window).mean()
        return df

    def detect(self, df):
        df = df.copy()

        # 1. Returns & Volatility
        df['returns'] = df['xau_close'].pct_change()
        df['vol'] = df['returns'].rolling(self.vol_window).std()
        df['vol_pct'] = df['vol'].rank(pct=True)

        # 2. ATR
        df = self.calculate_atr(df)

        # 3. SMA Slope (Trend detection)
        df['sma'] = df['xau_close'].rolling(self.trend_window).mean()
        df['sma_slope'] = df['sma'].diff()

        # 4. Default Regime = Range
        df['regime'] = 0

        # 5. Chaos: Top 10% Volatility
        df.loc[df['vol_pct'] > 0.90, 'regime'] = 2

        # 6. Trend: SMA slope above threshold & not in chaos
        slope_threshold = df['xau_close'].pct_change().rolling(self.trend_window).mean().abs()
        is_trend = (df['sma_slope'].abs() > slope_threshold) & (df['regime'] != 2)
        df.loc[is_trend, 'regime'] = 1

        # 7. Optional: Directional bias for Signal Generator
        df['bias'] = 0
        df.loc[df['regime'] == 1, 'bias'] = np.where(df['sma_slope'] > 0, 1, -1)

        return df[['xau_close', 'xau_high', 'xau_low', 'returns', 'vol', 'vol_pct', 'atr', 'sma', 'sma_slope', 'regime', 'bias']]
