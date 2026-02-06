# backend/core/validator.py

import pandas as pd
import numpy as np

class Validator:
    def __init__(self):
        # You can add any state initialization here
        pass

    def validate(self, df: pd.DataFrame, state: dict):
        """
        Validates signals and ensures chaos regimes are neutralized.
        Always preserves OHLC columns to prevent KeyErrors.
        """

        # Make a copy to avoid modifying original
        df = df.copy()

        # Ensure all essential columns exist
        for col in ["xau_open", "xau_high", "xau_low", "xau_close"]:
            if col not in df.columns:
                df[col] = np.nan

        # Example: zero out signals in chaos regimes
        if "regime" in df.columns and "signal" in df.columns:
            chaos_rows = df["regime"] == 2
            if chaos_rows.any():
                print(f"Validator: {chaos_rows.sum()} rows in chaos regime. Setting signals to 0.")
                df.loc[chaos_rows, "signal"] = 0

        # Fill any missing signals
        if "signal" in df.columns:
            df["signal"] = df["signal"].fillna(0)

        print("Validator: validation complete")
        return df
