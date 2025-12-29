from typing import Dict

from core.agents.base.agent import BaseAgent
from core.agents.base.result import AgentResult


class NoopAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="noop_agent", risk="low")

    def execute(self, action: str, args: Dict) -> Dict:
        # No-op: return success with echo
        return AgentResult(success=True, details={"action": action, "args": args}).to_dict()
