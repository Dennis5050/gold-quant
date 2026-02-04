import pandas as pd
import numpy as np

class BetaCalculator:
    """
    Computes Beta of a security relative to a benchmark.
    
    Beta = Covariance(asset, benchmark) / Variance(benchmark)
    """

    def __init__(self, window=60):
        """
        window: rolling window for beta calculation
        """
        self.window = window

    def compute_beta(self, asset_returns, benchmark_returns):
        """
        asset_returns: pd.Series of asset % returns
        benchmark_returns: pd.Series of benchmark % returns
        
        Returns a pd.Series of rolling beta values
        """
        if not isinstance(asset_returns, pd.Series) or not isinstance(benchmark_returns, pd.Series):
            raise ValueError("Inputs must be pandas Series")

        # Align the series
        df = pd.concat([asset_returns, benchmark_returns], axis=1).dropna()
        df.columns = ['asset', 'benchmark']

        # Rolling covariance and variance
        rolling_cov = df['asset'].rolling(self.window).cov(df['benchmark'])
        rolling_var = df['benchmark'].rolling(self.window).var()

        beta = rolling_cov / rolling_var
        return beta
