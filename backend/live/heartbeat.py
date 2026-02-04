# backend/live/heartbeat.py

import time
from datetime import datetime, timedelta

class Heartbeat:
    """
    Timing logic for live trading loops.
    Supports M15 (15-min) or H1 loops for checking signals and executing trades.
    """

    def __init__(self, timeframe="M15"):
        """
        timeframe: "M15" or "H1"
        """
        self.timeframe = timeframe
        self.interval = self._get_interval_seconds(timeframe)

    def _get_interval_seconds(self, timeframe):
        """Convert timeframe string to seconds"""
        if timeframe.upper() == "M15":
            return 15 * 60
        elif timeframe.upper() == "H1":
            return 60 * 60
        else:
            raise ValueError(f"Unsupported timeframe: {timeframe}")

    def wait_for_next_candle(self):
        """
        Wait until the next candle is complete.
        Returns the timestamp of the next candle.
        """
        now = datetime.utcnow()
        # Align to the next multiple of interval
        seconds_since_epoch = int(now.timestamp())
        next_candle_ts = ((seconds_since_epoch // self.interval) + 1) * self.interval
        wait_seconds = next_candle_ts - seconds_since_epoch

        if wait_seconds > 0:
            time.sleep(wait_seconds)

        next_candle_time = datetime.utcfromtimestamp(next_candle_ts)
        return next_candle_time

    def start_loop(self, callback):
        """
        Start a continuous heartbeat loop.
        `callback` is a function that runs every candle.
        """
        print(f"Starting live {self.timeframe} loop...")
        while True:
            next_candle = self.wait_for_next_candle()
            print(f"[Heartbeat] New candle at {next_candle}")
            try:
                callback()
            except Exception as e:
                print(f"[Heartbeat Error] {e}")
