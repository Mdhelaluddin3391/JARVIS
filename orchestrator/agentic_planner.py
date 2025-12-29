from typing import Dict, Any, Optional

from core.agents.registry import AgentRegistry


class AgenticPlanner:
    """Planner that can satisfy agent preconditions and orchestrate handoffs between agents.

    Usage:
      planner = AgenticPlanner(registry)
      planner.plan_and_execute({'action':'play','query':'jazz'})
    """

    def __init__(self, registry: Optional[AgentRegistry] = None):
        self.registry = registry

    def plan_and_execute(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        if not self.registry:
            return {"ok": False, "message": "no_registry"}

        # find candidate agent that can handle the intent
        agent = self.registry.find_agent_for_intent(intent)
        # fallback to mapping by name if none found
        if agent is None:
            # try by searching for common action names
            # registry users can pass an agent name directly in intent as 'agent'
            agent_name = intent.get("agent")
            if agent_name:
                agent = self.registry.get(agent_name)
        if agent is None:
            return {"ok": False, "message": "agent_not_found"}

        # check preconditions
        checker = getattr(agent, "check_precondition", None)
        if callable(checker):
            pre = checker(intent)
        else:
            pre = {"ok": True}

        if not pre.get("ok"):
            req = pre.get("requires")
            if req:
                helper_name = req.get("agent")
                sub_intent = req.get("intent")
                helper = self.registry.get(helper_name)
                if helper:
                    performer = getattr(helper, "perform", None)
                    if callable(performer):
                        res = performer(sub_intent)
                        if not res.get("ok"):
                            return {"ok": False, "message": f"failed_prereq:{res.get('message')}"}
                        performer_main = getattr(agent, "perform", None)
                        if callable(performer_main):
                            return performer_main(intent)
                        return {"ok": False, "message": "agent_cannot_perform"}
            return {"ok": False, "message": pre.get("reason", "precondition_failed")}

        performer_main = getattr(agent, "perform", None)
        if callable(performer_main):
            return performer_main(intent)
        return {"ok": False, "message": "agent_cannot_perform"}
