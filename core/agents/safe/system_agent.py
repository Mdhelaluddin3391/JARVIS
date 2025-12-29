import subprocess
from typing import Any, Dict, Optional

from core.agents.base.agent import BaseAgent
from permissions.approvals import ApprovalStore


class SystemAgent(BaseAgent):
    """System-level agent to perform privileged system actions.

    Uses an injected `ApprovalStore` for user confirmations and a `sys_runner` for executing OS commands (injectable for tests).
    """

    def __init__(self, approval_store: ApprovalStore, sys_runner: Optional[callable] = None, name: str = "system_agent", risk: str = "high"):
        super().__init__(name=name, risk=risk)
        self.approval_store = approval_store
        self.sys_runner = sys_runner or self._default_runner

    def can_handle(self, intent: Dict[str, Any]) -> bool:
        action = intent.get("action")
        return action in ("enable_wifi", "disable_wifi", "shutdown", "reboot")

    def check_precondition(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        action = intent.get("action")
        if action == "enable_wifi":
            if self._is_wifi_on():
                return {"ok": True}
            return {"ok": False, "requires": {"agent": self.name, "intent": {"action": "enable_wifi"}}}
        return {"ok": True}

    def perform(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        action = intent.get("action")
        if action == "enable_wifi":
            if not self.approval_store.request_approval("Allow Jarvis to enable WiFi?"):
                return {"ok": False, "message": "User denied enabling WiFi"}
            self._enable_wifi()
            return {"ok": True, "message": "WiFi enabled"}
        if action == "disable_wifi":
            if not self.approval_store.request_approval("Allow Jarvis to disable WiFi?"):
                return {"ok": False, "message": "User denied disabling WiFi"}
            self._disable_wifi()
            return {"ok": True, "message": "WiFi disabled"}
        if action == "shutdown":
            if not self.approval_store.request_approval("Confirm shutdown of this machine?"):
                return {"ok": False, "message": "Shutdown cancelled"}
            self._shutdown()
            return {"ok": True, "message": "Shutting down"}
        if action == "reboot":
            if not self.approval_store.request_approval("Confirm reboot of this machine?"):
                return {"ok": False, "message": "Reboot cancelled"}
            self._reboot()
            return {"ok": True, "message": "Rebooting"}
        return {"ok": False, "message": "Unknown action"}

    # Implement abstract BaseAgent.execute to satisfy abstract base class
    def execute(self, action: str, args: Dict) -> Dict:
        # translate older execute signature into perform-style intent dict
        intent = {}
        if isinstance(args, dict):
            intent.update(args)
        # allow action to be used as primary intent action
        intent.setdefault("action", action)
        return self.perform(intent)

    def _is_wifi_on(self) -> bool:
        try:
            res = subprocess.run(["nmcli", "-t", "-f", "WIFI", "g"], capture_output=True, text=True)
            return res.stdout.strip().lower() == "enabled"
        except Exception:
            return False

    def _enable_wifi(self):
        self.sys_runner("nmcli radio wifi on")

    def _disable_wifi(self):
        self.sys_runner("nmcli radio wifi off")

    def _shutdown(self):
        self.sys_runner("systemctl poweroff")

    def _reboot(self):
        self.sys_runner("systemctl reboot")

    def _default_runner(self, cmd: str):
        subprocess.run(cmd, shell=True, check=False)
