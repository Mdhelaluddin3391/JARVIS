from typing import Dict, List, Any


class TaskPlanner:
    """Simple task planner that maps intents to agent tasks.

    Returns a plan which is a list of task dicts: {"agent": str, "action": str, "args": {}}
    """

    INTENT_AGENT_MAP = {
        "shutdown_system": ("power_agent", "shutdown", "high"),
        "reboot_system": ("power_agent", "reboot", "high"),
        # manage_wifi now creates a multi-step plan: toggle wifi, then check network status
        "manage_wifi": ("wifi_agent", "toggle", "low"),
        "open_app": ("app_agent", "open", "low"),
        "play_music": ("music_agent", "play", "low"),
        # example intent that results in a multi-step plan
        "open_and_search": None,
    }

    def plan(self, parsed_intent: Dict[str, Any]) -> List[Dict]:
        intent = parsed_intent.get("intent")
        # Special-case multi-step expansions
        if intent == "manage_wifi":
            # primary: toggle wifi
            primary = {"agent": "wifi_agent", "action": "toggle", "args": {"text": parsed_intent.get("text")}, "agent_risk": "low"}
            # follow-up: check network status
            follow = {"agent": "network_agent", "action": "status", "args": {}, "agent_risk": "medium"}
            return [primary, follow]

        if intent == "open_and_search":
            ents = parsed_intent.get("entities", {})
            app = ents.get("app") or "browser"
            query = ents.get("query") or parsed_intent.get("text")
            return [
                {"agent": "app_agent", "action": "open", "args": {"app": app}, "agent_risk": "low"},
                {"agent": "search_agent", "action": "search", "args": {"q": query}, "agent_risk": "low"},
            ]

        entry = self.INTENT_AGENT_MAP.get(intent)
        if not entry:
            return []
        agent, action, risk = entry
        args = {"text": parsed_intent.get("text"), "entities": parsed_intent.get("entities", {})}
        return [{"agent": agent, "action": action, "args": args, "agent_risk": risk}]
