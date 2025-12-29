import time
from permissions.approvals import ApprovalStore


def test_approval_grant_and_is_approved(tmp_path):
    p = tmp_path / "approvals.jsonl"
    store = ApprovalStore(path=str(p))
    store.grant("power_agent", "shutdown", ttl_seconds=2)
    assert store.is_approved("power_agent", "shutdown") is True

    time.sleep(1.1)
    assert store.is_approved("power_agent", "shutdown") is True

    time.sleep(1.1)
    assert store.is_approved("power_agent", "shutdown") is False


def test_approval_wildcard(tmp_path):
    p = tmp_path / "approvals.jsonl"
    store = ApprovalStore(path=str(p))
    store.grant("wifi_agent", None, ttl_seconds=3600)
    assert store.is_approved("wifi_agent", "toggle") is True


def test_approval_persistence(tmp_path):
    p = tmp_path / "approvals.jsonl"
    store = ApprovalStore(path=str(p))
    store.grant("network_agent", "status", ttl_seconds=3600)

    # Create a new instance reading the same file
    store2 = ApprovalStore(path=str(p))
    assert store2.is_approved("network_agent", "status") is True
