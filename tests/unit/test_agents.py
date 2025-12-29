from core.agents.safe.wifi_agent import WifiAgent
from core.agents.privileged.power_agent import PowerAgent


def test_wifi_toggle():
    w = WifiAgent()
    res1 = w.execute("status", {})
    assert res1["success"] is True

    res2 = w.execute("toggle", {})
    assert res2["success"] is True
    assert res2["details"]["enabled"] is True

    res3 = w.execute("toggle", {})
    assert res3["details"]["enabled"] is False


def test_power_agent_simulated_actions():
    p = PowerAgent()
    res = p.execute("shutdown", {})
    assert res["success"] is True
    assert res["details"]["simulated"] is True

    res2 = p.execute("reboot", {})
    assert res2["success"] is True
