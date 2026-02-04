# backend/visuals/zones.py

import matplotlib.pyplot as plt

def plot_zones(ax, price_data, sl_prices, tp_prices):
    """
    Plot Stop-Loss (SL) and Take-Profit (TP) zones on a given matplotlib axis.
    
    Parameters:
    - ax: matplotlib axis to plot on
    - price_data: pandas Series of close prices
    - sl_prices: list or Series of stop-loss levels
    - tp_prices: list or Series of take-profit levels
    """
    for i, price in enumerate(price_data.index):
        # SL zone: red
        ax.axhline(y=sl_prices[i], color='red', linestyle='--', alpha=0.3)
        # TP zone: green
        ax.axhline(y=tp_prices[i], color='green', linestyle='--', alpha=0.3)

    ax.plot(price_data.index, price_data.values, color='blue', label='Price')
    ax.set_title("Price with SL/TP Zones")
    ax.set_xlabel("Time")
    ax.set_ylabel("Price")
    ax.legend()
    ax.grid(True)
