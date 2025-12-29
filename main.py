"""Simple CLI demo wiring perception -> orchestrator -> agents."""

from perception.perception_manager import PerceptionManager
from orchestrator.intent_parser import IntentParser
from orchestrator.task_planner import TaskPlanner
from core.agents.registry import AgentRegistry
from core.agents.safe.noop_agent import NoopAgent
from core.agents.safe.wifi_agent import WifiAgent
from core.agents.privileged.power_agent import PowerAgent
from core.orchestrator.event_bus import EventBus
from orchestrator.execution_manager import ExecutionManager
from permissions.policy_engine import PolicyEngine


def main_loop():
    print("JARVIS CLI demo. Type 'exit' to quit.")
    pm = PerceptionManager()
    ip = IntentParser()
    tp = TaskPlanner()
    registry = AgentRegistry()

    # register agents
    registry.register(NoopAgent().name, NoopAgent())
    registry.register(WifiAgent().name, WifiAgent())
    registry.register(PowerAgent().name, PowerAgent())
    # Register network agent so multi-step plans (wifi -> network status) succeed
    from core.agents.privileged.network_agent import NetworkAgent

    registry.register(NetworkAgent().name, NetworkAgent())

    # LLM-backed agent (uses local/remote adapters)
    from core.agents.safe.llm_agent import LLMAgent

    registry.register(LLMAgent().name, LLMAgent())

    # Music agent
    from core.agents.safe.music_agent import MusicAgent

    registry.register(MusicAgent().name, MusicAgent())

    eb = EventBus()
    policy = PolicyEngine()
    exec_mgr = ExecutionManager(registry, eb, policy_engine=policy)

    from orchestrator.router import Router

    router = Router(planner=tp)

    from orchestrator.confirmation import handle_confirmation

    def on_event(event):
        parsed = ip.parse(event)
        base_ctx = {"time_hour": 12, "battery": 0.8}
        r = router.route(parsed, context=base_ctx)
        if r["status"] == "no_plan":
            print(f"No plan: {r['reason']} for: {parsed}")
            return
        if r["status"] == "require_confirmation":
            print("Action requires confirmation:", r.get("needed"))
            res = handle_confirmation(parsed, router, exec_mgr, context=base_ctx)
            if res.get("status") == "confirmed":
                for rr in res.get("results", []):
                    print("->", rr)
            elif res.get("status") == "denied":
                print("User denied action.")
            else:
                print("Confirmation flow error:", res)
            return
        for task in r["plan"]:
            res = exec_mgr.execute_task(task, context=base_ctx)
            print("->", res)
            # voice feedback for music actions
            try:
                if speaker and res.get("success") and isinstance(res.get("result"), dict):
                    rr = res["result"]
                    status = rr.get("status")
                    if status == "playing":
                        track = rr.get("track") or rr.get("query")
                        speaker.speak(f"Playing {track}")
                    elif status == "fallback":
                        q = rr.get("query")
                        speaker.speak(f"Searching streaming platforms for {q}")
                    elif status == "stopped":
                        speaker.speak("Playback stopped")
                    elif status == "error":
                        speaker.speak(f"Error: {rr.get('reason')}")
            except Exception:
                pass

    pm.register_listener(on_event)

    speaker = None
    try:
        from voice.speaker import Speaker

        speaker = Speaker()
    except Exception:
        speaker = None

    while True:
        txt = input("You: ")
        if txt.strip().lower() in ("exit", "quit"):
            break
        # Demo: use the listener to normalize text (could be real STT in future)
        from voice.listener import Listener

        listener = Listener()
        text = listener.listen_from_text(txt)
        pm.emit_voice_event(text)

        # simple flow: if LLM agent answered, speak the response
        # when execution manager returns responses, they are printed above; we also speak them
        # Hook into exec_mgr by wrapping its execute_task is non-trivial here, instead speakers will be used in confirmation and response flows
        # For demo, if agent 'llm-agent' was used we will speak back inside exec_mgr results
        


if __name__ == "__main__":
    main_loop()
