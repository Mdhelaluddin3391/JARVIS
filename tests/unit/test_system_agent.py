from permissions.approvals import ApprovalStore
from core.agents.safe.system_agent import SystemAgent


def test_system_agent_enable_wifi_approved(monkeypatch):
    called = []

    def fake_confirmer(msg):
        called.append(msg)
        return True

    approval = ApprovalStore(confirmer=fake_confirmer)
    ran = []

    def fake_runner(cmd):
        ran.append(cmd)

    sa = SystemAgent(approval_store=approval, sys_runner=fake_runner)
    res = sa.perform({"action": "enable_wifi"})
    assert res["ok"] is True
    assert any("nmcli" in c or "radio wifi" in c for c in ran)
    assert called


def test_system_agent_enable_wifi_denied(monkeypatch):
    def fake_confirmer(msg):
        return False

    approval = ApprovalStore(confirmer=fake_confirmer)
    sa = SystemAgent(approval_store=approval, sys_runner=lambda c: None)
    res = sa.perform({"action": "enable_wifi"})
    assert res["ok"] is False
    assert "denied" in res["message"].lower()
