import pandas as pd
import numpy as np

class FeatureEngineer:
    def __init__(self, z_window=20, vol_window=100, atr_window=14):
        """
        z_window   : lookback for rolling Z-score
        vol_window : lookback for rolling volatility percentile
        atr_window : lookback for ATR calculation
        """
        self.z_window = z_window
        self.vol_window = vol_window
        self.atr_window = atr_window

    def calculate_atr(self, df):
        """Compute ATR for volatility-adjusted features"""
        df['high_low'] = df['xau_high'] - df['xau_low']
        df['high_close'] = (df['xau_high'] - df['xau_close'].shift()).abs()
        df['low_close'] = (df['xau_low'] - df['xau_close'].shift()).abs()
        df['tr'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
        df['atr'] = df['tr'].rolling(self.atr_window).mean()
        return df

    def rolling_zscore(self, series, window):
        """Compute rolling Z-score"""
        mean = series.rolling(window).mean()
        std = series.rolling(window).std()
        z = (series - mean) / std
        return z

    def calculate_volatility_percentile(self, series):
        """Compute rolling volatility percentile"""
        vol = series.rolling(self.vol_window).std()
        vol_pct = vol.rank(pct=True)
        return vol_pct

    def transform(self, df):
        """
        Input: dataframe with columns ['xau_close', 'xau_high', 'xau_low']
        Output: dataframe with engineered features
        """
        df = df.copy()

        # 1. Returns
        df['returns'] = df['xau_close'].pct_change()

        # 2. ATR
        df = self.calculate_atr(df)
        df['atr_norm'] = df['atr'] / df['xau_close']

        # 3. Z-score of price vs rolling SMA
        df['sma'] = df['xau_close'].rolling(self.z_window).mean()
        df['zscore'] = self.rolling_zscore(df['xau_close'], self.z_window)

        # 4. Rolling volatility percentile
        df['vol_pct'] = self.calculate_volatility_percentile(df['xau_close'])

        # 5. Optional momentum: normalized returns
        df['mom'] = df['returns'].rolling(self.z_window).mean() / df['returns'].rolling(self.z_window).std()

        # 6. Clean up
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        df.fillna(0, inplace=True)

        return df[['xau_close', 'xau_high', 'xau_low', 'returns', 'atr', 'atr_norm', 'sma', 'zscore', 'vol_pct', 'mom']]
