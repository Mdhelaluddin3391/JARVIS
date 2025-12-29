from typing import Dict, Optional

from core.orchestrator.event_bus import EventBus
from core.agents.registry import AgentRegistry
from permissions.policy_engine import PolicyEngine


class ExecutionManager:
    """Manage execution of planned tasks, including permission checks and event logging."""

    def __init__(self, registry: AgentRegistry, event_bus: EventBus, policy_engine: Optional[PolicyEngine] = None):
        self.registry = registry
        self.event_bus = event_bus
        self.policy_engine = policy_engine

    def execute_task(self, task: Dict, context: Dict = None) -> Dict:
        agent_name = task.get("agent")
        action = task.get("action")
        args = task.get("args", {})

        self.event_bus.append_event({"type": "task.start", "task": task, "context": context})

        agent = self.registry.get(agent_name)
        if not agent:
            result = {"success": False, "error": "agent_not_found"}
            self.event_bus.append_event({"type": "task.end", "task": task, "result": result})
            return result

        # Policy evaluation
        if self.policy_engine:
            # augment context with agent metadata
            ctx = dict(context or {})
            ctx.setdefault("agent_risk", getattr(agent, "risk", "low"))
            allowed, reason = self.policy_engine.evaluate(task, ctx)
            self.event_bus.append_event({"type": "task.policy", "task": task, "allowed": allowed, "reason": reason})
            if not allowed:
                result = {"success": False, "error": "policy_denied", "reason": reason}
                self.event_bus.append_event({"type": "task.end", "task": task, "result": result})
                return result

        try:
            res = agent.execute(action, args)
            result = {"success": True, "result": res}
        except Exception as e:
            result = {"success": False, "error": str(e)}

        self.event_bus.append_event({"type": "task.end", "task": task, "result": result})
        return result
