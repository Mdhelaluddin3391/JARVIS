from core.agents.registry import AgentRegistry
from core.agents.safe.system_agent import SystemAgent
from core.agents.safe.music_agent import MusicAgent
from orchestrator.agentic_planner import AgenticPlanner
from permissions.approvals import ApprovalStore


def test_planner_handoff_enable_wifi(tmp_path):
    registry = AgentRegistry()
    approval = ApprovalStore(confirmer=lambda m: True)
    system = SystemAgent(approval_store=approval, sys_runner=lambda c: None)
    music = MusicAgent(music_dir=str(tmp_path / "empty"))
    registry.register(system.name, system)
    registry.register(music.name, music)

    planner = AgenticPlanner(registry=registry)

    intent = {"action": "play", "query": "lofi"}
    res = planner.plan_and_execute(intent)
    assert res["ok"] is True
    assert res.get("type") == "stream"
    assert "youtube" in res.get("provider")
