# backend/core/feature_engineer.py

import pandas as pd
import numpy as np

class FeatureEngineer:
    """
    Add technical features to the dataset.
    """

    def add_features(self, df):
        # Ensure we have a close price column
        if 'xau_close' not in df.columns:
            raise ValueError("Data must contain 'xau_close' column")

        # Example features
        df = df.copy()  # avoid chained assignment warnings

        # Simple moving averages
        df['sma_5'] = df['xau_close'].rolling(5).mean()
        df['sma_10'] = df['xau_close'].rolling(10).mean()
        df['sma_diff'] = df['sma_5'] - df['sma_10']

        # Returns
        df['returns'] = df['xau_close'].pct_change()

        # Volatility
        df['volatility_5'] = df['returns'].rolling(5).std()
        df['volatility_10'] = df['returns'].rolling(10).std()

        # Fill NaNs for testing
        df.fillna(0, inplace=True)

        return df
