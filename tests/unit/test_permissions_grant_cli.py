from permissions.cli import grant_approval, list_approvals
from permissions.approvals import ApprovalStore


def test_grant_approval(tmp_path):
    p = tmp_path / "approvals.jsonl"
    # grant 1 hour
    grant_approval("demo_agent", "action1", hours=1, path=str(p))

    store = ApprovalStore(path=str(p))
    assert store.is_approved("demo_agent", "action1") is True

    active = list_approvals(path=str(p))
    assert any(k.startswith("demo_agent:action1") for k in active.keys())
