# backend/visuals/equity_curve.py

import matplotlib.pyplot as plt
import pandas as pd

def plot_equity_curve(equity_series, title="Equity Curve"):
    """
    Plots the equity curve over time.

    Parameters:
    - equity_series: pandas Series or list of equity values
    - title: plot title
    """
    if not isinstance(equity_series, pd.Series):
        equity_series = pd.Series(equity_series)

    plt.figure(figsize=(10, 5))
    plt.plot(equity_series.index, equity_series.values, color='blue', linewidth=2)
    plt.fill_between(equity_series.index, equity_series.values, color='lightblue', alpha=0.3)
    plt.title(title)
    plt.xlabel("Time")
    plt.ylabel("Equity")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_drawdown(equity_series, title="Drawdown"):
    """
    Plots the drawdown curve (equity decline from peak).

    Parameters:
    - equity_series: pandas Series of equity values
    """
    if not isinstance(equity_series, pd.Series):
        equity_series = pd.Series(equity_series)

    peak = equity_series.cummax()
    drawdown = (equity_series - peak) / peak

    plt.figure(figsize=(10, 5))
    plt.plot(drawdown.index, drawdown.values, color='red', linewidth=2)
    plt.fill_between(drawdown.index, drawdown.values, color='pink', alpha=0.3)
    plt.title(title)
    plt.xlabel("Time")
    plt.ylabel("Drawdown (%)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
