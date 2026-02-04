# backend/live/mt5_connector.py

import logging

class MT5Connector:
    """
    MT5 Connector for live or paper trading.
    Currently supports paper mode simulation.
    """

    def __init__(self, mode="paper", symbols=None):
        """
        mode: "paper" or "live"
        symbols: list of symbols to check (e.g., ["XAUUSD", "DXY"])
        """
        self.mode = mode
        self.symbols = symbols or ["XAUUSD"]
        self.logger = logging.getLogger("MT5Connector")
        self.connected = False
        self._connect()

    def _connect(self):
        """
        Connect to MT5 terminal or setup paper mode.
        """
        if self.mode == "paper":
            self.logger.info("Running in PAPER mode. No real MT5 connection required.")
            self.connected = True
        else:
            # TODO: Add real MT5 connection logic using MetaTrader5 package
            # Example: mt5.initialize()
            raise NotImplementedError("Live MT5 connection not implemented yet")

    def check_symbols(self):
        """
        Verify all required symbols are available.
        Returns dict {symbol: True/False}
        """
        status = {}
        for sym in self.symbols:
            # In paper mode, assume all symbols are valid
            status[sym] = True
        self.logger.info(f"Symbols status: {status}")
        return status

    def disconnect(self):
        """
        Cleanly disconnect from MT5 if live mode.
        """
        if self.mode != "paper":
            # mt5.shutdown()
            self.connected = False
            self.logger.info("Disconnected from MT5")
