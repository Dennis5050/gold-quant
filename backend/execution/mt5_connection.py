import MetaTrader5 as mt5

def connect():
    if not mt5.initialize():
        raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")
    print("MT5 connected")

def shutdown():
    mt5.shutdown()
