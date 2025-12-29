from permissions.policy_engine import PolicyEngine


def test_time_block_rule():
    engine = PolicyEngine(blocked_hours=(2, 4))
    task = {"agent": "wifi_agent", "action": "toggle"}
    ok, reason = engine.evaluate(task, {"time_hour": 3})
    assert ok is False
    assert "restricted" in reason


def test_battery_shutdown_requires_confirm():
    engine = PolicyEngine()
    task = {"agent": "power_agent", "action": "shutdown"}
    ok, reason = engine.evaluate(task, {"battery": 0.01})
    assert ok is False
    assert reason == "battery_too_low"


def test_high_risk_confidence_rule():
    engine = PolicyEngine()
    task = {"agent": "power_agent", "action": "shutdown"}
    ok, reason = engine.evaluate(task, {"user_confidence": 0.5, "agent_risk": "high"})
    assert ok is False
    assert "low_user_confidence" in reason


def test_allow_with_confirmation():
    engine = PolicyEngine()
    task = {"agent": "power_agent", "action": "shutdown"}
    ok, reason = engine.evaluate(task, {"user_confidence": 0.5, "agent_risk": "high", "user_confirmed": True})
    assert ok is True
