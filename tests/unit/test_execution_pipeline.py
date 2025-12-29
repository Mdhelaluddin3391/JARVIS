from core.orchestrator.event_bus import EventBus
from core.agents.registry import AgentRegistry
from core.agents.safe.noop_agent import NoopAgent
from orchestrator.execution_manager import ExecutionManager
from permissions.policy_engine import PolicyEngine


def test_execution_pipeline(tmp_path):
    path = tmp_path / "events.jsonl"
    eb = EventBus(path=str(path))
    registry = AgentRegistry()

    noop = NoopAgent()
    registry.register(noop.name, noop)

    manager = ExecutionManager(registry, eb)

    task = {"agent": "noop_agent", "action": "test", "args": {"k": "v"}}
    res = manager.execute_task(task)
    assert res["success"] is True

    events = list(eb.read_events())
    # Should have start and end events
    types = [e["event"]["type"] for e in events]
    assert "task.start" in types
    assert "task.end" in types


def test_policy_blocks_high_risk(tmp_path):
    path = tmp_path / "events.jsonl"
    eb = EventBus(path=str(path))
    registry = AgentRegistry()

    noop = NoopAgent()
    registry.register(noop.name, noop)

    # PolicyEngine that blocks hour 2..4
    policy = PolicyEngine(blocked_hours=(2, 4))
    manager = ExecutionManager(registry, eb, policy_engine=policy)

    task = {"agent": "noop_agent", "action": "test"}
    # Block by time
    res = manager.execute_task(task, context={"time_hour": 3})
    assert res["success"] is False
    assert res["error"] == "policy_denied"

    # Allow when outside blocked time
    res2 = manager.execute_task(task, context={"time_hour": 6})
    assert res2["success"] is True
