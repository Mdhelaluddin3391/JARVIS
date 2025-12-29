import json
import os
import time
from typing import Dict, Optional


class ApprovalStore:
    """Stores persistent approvals for (agent, action) with expiry timestamps.

    Simple file-backed store for prototype. Approvals are keyed by `agent:action`.

    Optionally accepts a `confirmer` callable for runtime interactive approvals (e.g., voice or console).
    The callable signature is `confirmer(message: str) -> bool`.
    """

    def __init__(self, path: str = "data/approvals.jsonl", confirmer=None):
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self._store: Dict[str, float] = {}
        self._confirmer = confirmer
        self._load()

    def request_approval(self, message: str) -> bool:
        """Request runtime approval via configured confirmer, returns True if approved."""
        if callable(self._confirmer):
            try:
                return bool(self._confirmer(message))
            except Exception:
                return False
        # No runtime confirmer available; default to False (deny)
        return False

    def _load(self):
        if not os.path.exists(self.path):
            return
        try:
            with open(self.path, "r", encoding="utf-8") as fh:
                for line in fh:
                    try:
                        rec = json.loads(line)
                        key = rec.get("key")
                        action = rec.get("action", "grant")
                        if not key:
                            continue
                        if action == "grant":
                            exp = rec.get("expiry")
                            if exp:
                                self._store[key] = float(exp)
                        elif action == "revoke":
                            if key in self._store:
                                del self._store[key]
                    except json.JSONDecodeError:
                        continue
        except Exception:
            # best-effort; on failure, start with empty store
            self._store = {}

    def _persist_record(self, key: str, expiry: Optional[float] = None, action: str = "grant") -> None:
        rec = {"key": key, "action": action}
        if expiry is not None:
            rec["expiry"] = expiry
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec) + "\n")

    @staticmethod
    def _make_key(agent: str, action: Optional[str]) -> str:
        return f"{agent}:{action or '*'}"

    def grant(self, agent: str, action: Optional[str], ttl_seconds: int) -> None:
        key = self._make_key(agent, action)
        expiry = time.time() + int(ttl_seconds)
        self._store[key] = expiry
        self._persist_record(key, expiry, action="grant")

    def is_approved(self, agent: str, action: Optional[str]) -> bool:
        # Check specific agent:action first, then agent:* wildcard
        now = time.time()
        key = self._make_key(agent, action)
        exp = self._store.get(key)
        if exp and exp > now:
            return True
        # wildcard
        key2 = self._make_key(agent, None)
        exp2 = self._store.get(key2)
        if exp2 and exp2 > now:
            return True
        return False

    def revoke(self, agent: str, action: Optional[str] = None) -> None:
        key = self._make_key(agent, action)
        if key in self._store:
            del self._store[key]
        # Persist a revocation entry so it will be applied when reloading
        self._persist_record(key, expiry=None, action="revoke")

    def list_active(self) -> Dict[str, float]:
        now = time.time()
        return {k: v for k, v in self._store.items() if v > now}
