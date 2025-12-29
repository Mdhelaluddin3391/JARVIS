from orchestrator.task_planner import TaskPlanner
from core.agents.registry import AgentRegistry
from core.agents.safe.wifi_agent import WifiAgent
from core.agents.privileged.network_agent import NetworkAgent
from core.orchestrator.event_bus import EventBus
from orchestrator.execution_manager import ExecutionManager


def test_manage_wifi_multi_step(tmp_path):
    registry = AgentRegistry()
    w = WifiAgent()
    n = NetworkAgent()
    registry.register(w.name, w)
    registry.register(n.name, n)

    eb = EventBus(path=str(tmp_path / "events.jsonl"))
    exec_mgr = ExecutionManager(registry, eb)

    planner = TaskPlanner()
    plan = planner.plan({"intent": "manage_wifi", "text": "wifi toggle"})
    assert len(plan) == 2

    # execute plan steps sequentially
    results = []
    for t in plan:
        res = exec_mgr.execute_task(t, context={"time_hour": 12, "battery": 0.9})
        results.append(res)

    # both steps should have been executed successfully
    assert all(r.get("success") for r in results)

    # verify events: there should be task.start and task.end for both tasks
    events = list(eb.read_events())
    types = [e["event"]["type"] for e in events]
    assert types.count("task.start") == 2
    assert types.count("task.end") == 2
