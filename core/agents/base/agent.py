from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseAgent(ABC):
    """Base agent class for all agents.

    Agents should be single-responsibility and implement `execute`.
    """

    def __init__(self, name: str, risk: str = "low", permissions: Dict[str, Any] = None):
        self.name = name
        self.risk = risk
        self.permissions = permissions or {}

    @abstractmethod
    def execute(self, action: str, args: Dict) -> Dict:
        """Execute an action and return a result dict."""
        raise NotImplementedError
