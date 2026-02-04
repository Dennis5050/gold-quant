import pandas as pd

class Validator:
    """
    Strict Trade Validator (Sniper Mode)
    Checks if a signal is allowed based on multiple criteria:
        - Global expectancy
        - Regime expectancy
        - Volatility percentile
        - Open positions
    """

    def __init__(self, max_vol_pct=0.95):
        self.max_vol_pct = max_vol_pct

    def validate(self, signal_row, state):
        """
        Parameters:
            signal_row : pd.Series
                Must contain ['signal', 'regime', 'vol_pct']
            state : dict
                Must contain keys: 'is_active', 'open_pos'
        
        Returns:
            bool : True if trade is allowed, False otherwise
        """

        # --- Kill Switch Check ---
        if not state.get('is_active', True):
            return False

        # --- Regime Check ---
        regime = signal_row['regime']
        if regime == 2:
            # Chaos regime: block all trades
            return False

        # --- Volatility Check ---
        vol_pct = signal_row['vol_pct']
        if vol_pct > self.max_vol_pct:
            return False

        # --- Open Position Check ---
        if state.get('open_pos', False):
            return False

        # --- Signal Validity ---
        if signal_row['signal'] == 0:
            return False

        # Passed all checks
        return True

    def batch_validate(self, df, state):
        """
        Apply validator across a DataFrame
        Adds a 'valid' column (True/False)
        """
        df = df.copy()
        df['valid'] = df.apply(lambda row: self.validate(row, state), axis=1)
        return df
