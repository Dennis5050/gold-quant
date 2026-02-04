# backend/core/validator.py

import pandas as pd
import numpy as np

class Validator:
    """
    Simple validator for signals and data integrity.
    """

    def validate(self, data: pd.DataFrame, state: dict):
        """
        Validates signals based on regime and other conditions.
        Args:
            data: DataFrame containing 'signal' and 'regime'
            state: dictionary to maintain any validation state
        """
        df = data.copy()

        # Ensure necessary columns exist
        required_cols = ['signal', 'regime']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing column '{col}' for validation")

        # --- Vectorized validation ---
        # In chaos regime (2), signals should be flat (0)
        chaos_mask = df['regime'] == 2
        if chaos_mask.any():
            print(f"Validator: {chaos_mask.sum()} rows in chaos regime. Setting signals to 0.")
            df.loc[chaos_mask, 'signal'] = 0

        # You can add more validation rules here...
        # Example: clamp signals to allowed set [-1, 0, 1]
        df['signal'] = df['signal'].clip(-1, 1)

        print("Validator: validation complete")
        return df
