# backend/tests/test_validator.py
import pandas as pd
import numpy as np
from core.validator import Validator

def test_all_gates_true():
    validator = Validator()
    df = pd.DataFrame({
        "signal": [1, -1, 0],
        "regime": [0,1,2],
        "vol_pct": [0.1,0.2,0.3]
    })
    results = df.apply(lambda row: validator.validate(row["signal"], row["regime"], row["vol_pct"]), axis=1)
    
    # Should return a boolean series
    assert all([isinstance(x, bool) for x in results])
