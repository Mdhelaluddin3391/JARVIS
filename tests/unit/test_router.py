from orchestrator.intent_parser import IntentParser
from orchestrator.router import Router
from orchestrator.task_planner import TaskPlanner


def test_router_requires_confirmation_for_low_confidence_high_risk():
    ip = IntentParser()
    parsed = ip.parse({"text": "Shutdown system now", "confidence": 0.5})

    # make planner map shutdown_system to power_agent (high risk)
    planner = TaskPlanner()
    router = Router(planner=planner, confirmation_threshold=0.85)

    res = router.route(parsed, context={})
    assert res["status"] == "require_confirmation"


def test_router_routes_wifi():
    ip = IntentParser()
    parsed = ip.parse({"text": "wifi toggle", "confidence": 0.95})
    planner = TaskPlanner()
    router = Router(planner=planner)

    res = router.route(parsed, context={})
    assert res["status"] == "ok"
    assert res["plan"]
    assert res["plan"][0]["agent"] == "wifi_agent"


def test_router_handles_unknown():
    ip = IntentParser()
    parsed = ip.parse({"text": "gibberish stuff", "confidence": 0.6})
    planner = TaskPlanner()
    router = Router(planner=planner)

    res = router.route(parsed, context={})
    assert res["status"] == "no_plan"
