from orchestrator.intent_parser import IntentParser
from orchestrator.router import Router
from orchestrator.task_planner import TaskPlanner
from core.agents.registry import AgentRegistry
from core.agents.safe.music_agent import MusicAgent
from core.orchestrator.event_bus import EventBus
from orchestrator.execution_manager import ExecutionManager
from permissions.policy_engine import PolicyEngine


def test_voice_activation_flow(monkeypatch, tmp_path):
    # Register music agent and simulate a local track
    music_dir = tmp_path / "Music"
    music_dir.mkdir()
    song = music_dir / "test song.mp3"
    song.write_text("fake")

    monkeypatch.setenv("MUSIC_DIR", str(music_dir))

    registry = AgentRegistry()
    registry.register(MusicAgent().name, MusicAgent())
    eb = EventBus(str(tmp_path / "events.jsonl"))
    policy = PolicyEngine()
    exec_mgr = ExecutionManager(registry, eb, policy_engine=policy)

    # Simulate parsing and routing a voice command
    ip = IntentParser()
    parsed = ip.parse({"text": "Hi Jarvis, play test song", "confidence": 0.98})
    router = Router(planner=TaskPlanner(), registry=registry)
    r = router.route(parsed, context={})
    assert r["status"] == "ok"
    assert r["plan"]

    # Execute plan
    for task in r["plan"]:
        res = exec_mgr.execute_task(task, context={})
        assert res["success"] is True
