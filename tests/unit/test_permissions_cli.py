from permissions.cli import list_approvals, revoke_approval
from permissions.approvals import ApprovalStore


def test_cli_list_and_revoke(tmp_path):
    p = tmp_path / "approvals.jsonl"
    store = ApprovalStore(path=str(p))
    store.grant("power_agent", "shutdown", ttl_seconds=3600)

    active = list_approvals(path=str(p))
    assert any(k.startswith("power_agent:shutdown") or k == "power_agent:shutdown" for k in active.keys())

    existed = revoke_approval("power_agent", "shutdown", path=str(p))
    assert existed is True

    active2 = list_approvals(path=str(p))
    assert not any(k.startswith("power_agent:shutdown") for k in active2.keys())
