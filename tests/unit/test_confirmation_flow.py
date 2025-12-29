from orchestrator.intent_parser import IntentParser
from orchestrator.router import Router
from orchestrator.task_planner import TaskPlanner
from orchestrator.confirmation import handle_confirmation
from core.agents.registry import AgentRegistry
from core.agents.privileged.power_agent import PowerAgent
from core.orchestrator.event_bus import EventBus
from orchestrator.execution_manager import ExecutionManager


def test_confirmation_accepts_and_executes(tmp_path):
    parsed = {"intent": "shutdown_system", "confidence": 0.4, "text": "shutdown now"}
    registry = AgentRegistry()
    p = PowerAgent()
    registry.register(p.name, p)

    eb = EventBus(path=str(tmp_path / "events.jsonl"))
    exec_mgr = ExecutionManager(registry, eb)
    planner = TaskPlanner()
    router = Router(planner=planner, registry=registry, confirmation_threshold=0.85)

    # Simulate user typing 'y'
    res = handle_confirmation(parsed, router, exec_mgr, context={"time_hour": 12}, input_fn=lambda prompt: "y")
    assert res["status"] == "confirmed"
    assert len(res["results"]) == 1
    assert res["results"][0]["success"] is True

    events = list(eb.read_events())
    assert any(e["event"]["type"] == "task.start" for e in events)


def test_confirmation_denied_no_execution(tmp_path):
    parsed = {"intent": "shutdown_system", "confidence": 0.4, "text": "shutdown now"}
    registry = AgentRegistry()
    p = PowerAgent()
    registry.register(p.name, p)

    eb = EventBus(path=str(tmp_path / "events.jsonl"))
    exec_mgr = ExecutionManager(registry, eb)
    planner = TaskPlanner()
    router = Router(planner=planner, registry=registry, confirmation_threshold=0.85)

    # Simulate user typing 'n'
    res = handle_confirmation(parsed, router, exec_mgr, context={"time_hour": 12}, input_fn=lambda prompt: "n")
    assert res["status"] == "denied"

    events = list(eb.read_events())
    # No task.start should have been appended
    assert not any(e["event"]["type"] == "task.start" for e in events)
