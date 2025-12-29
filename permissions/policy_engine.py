from typing import Dict, Tuple


class PolicyEngine:
    """Minimal policy engine prototype with a few example rules.

    Rules are evaluated in order; the first deny stops the action. Returns (allowed: bool, reason: str)
    """

    def __init__(self, blocked_hours: Tuple[int, int] = (2, 4)):
        # blocked_hours: tuple(start_hour, end_hour) 24h format where some operations are restricted
        self.blocked_hours = blocked_hours

    def evaluate(self, task: Dict, context: Dict) -> Tuple[bool, str]:
        # Basic structure for tasks: {"agent": "power_agent", "action": "shutdown", "args": {}}
        # Context may include: time_hour (0-23), battery (0.0-1.0), user_confidence (0.0-1.0), user_confirmed (bool), agent_risk
        t = context or {}
        agent = task.get("agent")
        action = task.get("action")

        # Time-based rule
        hour = t.get("time_hour")
        if hour is not None:
            start, end = self.blocked_hours
            if start <= hour < end:
                return False, f"action restricted during hours {start}-{end}"

        # Battery rule example: don't allow shutdown if battery critically low and user hasn't confirmed
        battery = t.get("battery")
        if agent == "power_agent" and action in ("shutdown", "reboot"):
            if battery is not None and battery < 0.05 and not t.get("user_confirmed"):
                return False, "battery_too_low"

        # Confidence / trust rule
        user_conf = t.get("user_confidence", 1.0)
        agent_risk = t.get("agent_risk", "low")
        if agent_risk == "high" and user_conf < 0.85 and not t.get("user_confirmed"):
            return False, "low_user_confidence_for_high_risk_action"

        return True, "ok"
