from typing import Dict, Optional


class AgentRegistry:
    """Simple agent registry for registering and retrieving agents by name.

    Agents may expose optional metadata like `priority` which will be used by the Router to
    prioritize execution order when multiple tasks are present.
    """

    def __init__(self):
        self._agents: Dict[str, object] = {}

    def register(self, name: str, agent: object) -> None:
        self._agents[name] = agent

    def get(self, name: str):
        return self._agents.get(name)

    def list_agents(self):
        return list(self._agents.keys())

    def agent_priority(self, name: str) -> int:
        a = self.get(name)
        if a is None:
            return 0
        return int(getattr(a, "priority", 0))

    def has_agent(self, name: str) -> bool:
        return name in self._agents

    def find_agent_for_intent(self, intent: dict):
        """Return the first registered agent object whose `can_handle` method returns True for the intent.

        Agents that do not implement `can_handle` are ignored. Returns None if not found.
        """
        for a in self._agents.values():
            try:
                can = getattr(a, "can_handle", None)
                if callable(can) and can(intent):
                    return a
            except Exception:
                continue
        return None