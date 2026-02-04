import pandas as pd
import numpy as np

class SignalGenerator:
    def __init__(self, z_thresh=1.0, mom_thresh=0.0):
        """
        z_thresh : Z-score threshold for triggering trades
        mom_thresh: minimum momentum required for trend trades
        """
        self.z_thresh = z_thresh
        self.mom_thresh = mom_thresh

    def generate(self, df):
        """
        Input: df with features ['zscore', 'mom', 'vol_pct', 'regime']
        Output: df with 'signal' column: 1=Buy, -1=Sell, 0=Flat
        """
        df = df.copy()
        df['signal'] = 0  # Default Flat

        for idx, row in df.iterrows():
            regime = row['regime']
            z = row['zscore']
            mom = row['mom']
            vol_pct = row['vol_pct']

            # Chaos regime: no trades
            if regime == 2 or vol_pct > 0.95:
                df.at[idx, 'signal'] = 0
                continue

            # Trend regime: pullbacks in momentum direction
            if regime == 1:
                if z < -self.z_thresh and mom > self.mom_thresh:
                    df.at[idx, 'signal'] = 1  # Buy
                elif z > self.z_thresh and mom < -self.mom_thresh:
                    df.at[idx, 'signal'] = -1  # Sell

            # Range regime: mean reversion
            elif regime == 0:
                if z < -self.z_thresh:
                    df.at[idx, 'signal'] = 1  # Buy
                elif z > self.z_thresh:
                    df.at[idx, 'signal'] = -1  # Sell

        return df[['zscore', 'mom', 'vol_pct', 'regime', 'signal']]
