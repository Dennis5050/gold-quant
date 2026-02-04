# backend/tests/test_risk.py
import pytest
from risk import RiskManager, KillSwitch

def test_position_size_calculation():
    rm = RiskManager(account_equity=100000, risk_per_trade=0.01)
    size = rm.calculate_position_size(entry_price=2000, stop_loss_price=1990)
    
    # Should return a positive float
    assert size > 0
    assert isinstance(size, float)

def test_sl_tp_calculation():
    rm = RiskManager()
    sl, tp = rm.apply_sl_tp(entry_price=2000, direction=1, atr=10)
    
    assert sl < 2000
    assert tp > 2000

def test_kill_switch():
    ks = KillSwitch(max_drawdown_pct=0.2, min_expectancy=0.1)
    ks.reset(100000)
    
    # Test equity below drawdown
    assert ks.is_system_active(90000, 0.2)  # 10% drawdown, should be True
    assert not ks.is_system_active(75000, 0.2)  # 25% drawdown, exceeds 20%
    
    # Test expectancy check
    assert not ks.is_system_active(100000, 0.05)  # expectancy below 0.1
