from typing import Dict, List, Optional

from orchestrator.task_planner import TaskPlanner
from core.agents.registry import AgentRegistry


class Router:
    """Route parsed intents to plans, handle disambiguation, confirmation prompts, and prioritization.

    Enhancements:
    - Accepts an AgentRegistry to consult agent metadata (priority)
    - Supports routing preferences via `context["prefer_agent"]` or `context["prefer_local"]`
    - Reorders multi-step plans by agent priority and preferences
    """

    def __init__(self, planner: Optional[TaskPlanner] = None, registry: Optional[AgentRegistry] = None, confirmation_threshold: float = 0.85):
        self.planner = planner or TaskPlanner()
        self.confirmation_threshold = confirmation_threshold
        self.registry = registry or AgentRegistry()

    def _apply_preferences(self, plan: List[Dict], context: Dict) -> List[Dict]:
        # Move preferred agent tasks to the front, then sort by agent priority
        prefer_agent = context.get("prefer_agent")

        def score(task: Dict) -> int:
            name = task.get("agent")
            base = self.registry.agent_priority(name)
            # boost if preferred
            boost = 5 if prefer_agent and name == prefer_agent else 0
            return base + boost

        return sorted(plan, key=score, reverse=True)

    def route(self, parsed_intent: Dict, context: Dict = None) -> Dict:
        p = parsed_intent or {}
        ctx = context or {}

        intent = p.get("intent", "unknown")
        confidence = p.get("confidence", 0.0)

        if intent == "unknown":
            return {"status": "no_plan", "reason": "unknown_intent", "plan": []}

        plan = self.planner.plan(p)
        if not plan:
            return {"status": "no_plan", "reason": "planner_empty", "plan": []}

        # Confirmation check for any high risk task
        # If an approval exists for the agent/action, skip confirmation
        from permissions.approvals import ApprovalStore

        store = ApprovalStore()
        for t in plan:
            agent_risk = ctx.get("agent_risk") or t.get("agent_risk") or "low"
            agent_name = t.get("agent")
            action_name = t.get("action")
            if agent_risk == "high" and not ctx.get("user_confirmed"):
                if store.is_approved(agent_name, action_name):
                    # approved, continue without requiring explicit confirmation
                    continue
                return {"status": "require_confirmation", "reason": "low_confidence_for_high_risk", "needed": {"intent": intent, "confidence": confidence}}

        # Apply preferences and prioritization
        ordered = self._apply_preferences(plan, ctx)

        return {"status": "ok", "plan": ordered}
