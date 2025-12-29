from typing import Dict

from core.agents.base.agent import BaseAgent
from core.agents.base.result import AgentResult


class WifiAgent(BaseAgent):
    _enabled = False

    def __init__(self):
        super().__init__(name="wifi_agent", risk="low")

    def execute(self, action: str, args: Dict) -> Dict:
        if action == "toggle":
            WifiAgent._enabled = not WifiAgent._enabled
            return AgentResult(success=True, details={"enabled": WifiAgent._enabled}).to_dict()
        if action == "status":
            return AgentResult(success=True, details={"enabled": WifiAgent._enabled}).to_dict()
        return AgentResult(success=False, details={"error": "unknown_action"}).to_dict()
