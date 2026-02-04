# backend/tests/test_regime.py
import pandas as pd
import numpy as np
from core.regime_detector import RegimeDetector

def create_dummy_data():
    """Generate 200 candles of dummy XAUUSD data"""
    np.random.seed(42)
    prices = np.cumsum(np.random.randn(200)) + 2000  # starting around 2000
    df = pd.DataFrame({
        "xau_close": prices
    })
    return df

def test_detect_regime_output():
    df = create_dummy_data()
    detector = RegimeDetector(vol_window=20)
    df_out = detector.detect(df)
    
    # Check regime column exists
    assert "regime" in df_out.columns
    
    # Regimes should be only 0,1,2
    assert df_out["regime"].isin([0,1,2]).all()
    
    # Volatility percentile column exists
    assert "vol_pct" in df_out.columns
