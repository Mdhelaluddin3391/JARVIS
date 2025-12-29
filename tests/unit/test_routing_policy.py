from orchestrator.intent_parser import IntentParser
from orchestrator.router import Router
from orchestrator.task_planner import TaskPlanner
from core.agents.registry import AgentRegistry
from core.agents.safe.wifi_agent import WifiAgent
from core.agents.privileged.network_agent import NetworkAgent


def test_plan_ordering_by_priority():
    ip = IntentParser()
    parsed = ip.parse({"text": "wifi toggle", "confidence": 0.95})

    planner = TaskPlanner()
    registry = AgentRegistry()
    w = WifiAgent()
    net = NetworkAgent()
    # assign priorities
    w.priority = 10
    net.priority = 5

    registry.register(w.name, w)
    registry.register(net.name, net)

    router = Router(planner=planner, registry=registry)
    res = router.route(parsed, context={})
    assert res["status"] == "ok"
    # After planning, first task should be wifi_agent (priority 10)
    assert res["plan"][0]["agent"] == "wifi_agent"


def test_prefer_agent_moves_it_first():
    ip = IntentParser()
    parsed = ip.parse({"text": "wifi toggle", "confidence": 0.95})

    planner = TaskPlanner()
    registry = AgentRegistry()
    w = WifiAgent()
    net = NetworkAgent()
    w.priority = 1
    net.priority = 1

    registry.register(w.name, w)
    registry.register(net.name, net)

    router = Router(planner=planner, registry=registry)
    # prefer network_agent -> should move network_agent task first
    res = router.route(parsed, context={"prefer_agent": "network_agent"})
    assert res["status"] == "ok"
    assert res["plan"][0]["agent"] == "network_agent"
