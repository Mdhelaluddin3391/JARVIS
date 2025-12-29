from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class AgentResult:
    success: bool
    details: Dict = None

    def to_dict(self):
        return {"success": self.success, "details": self.details or {}}
