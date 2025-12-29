import json
import os
import time
import uuid
from typing import Dict, Generator, Optional, List


class EventBus:
    """Append-only event bus backed by a JSONL file.

    - Validates basic event schema (must be a dict containing `type`).
    - Uses fsync after appends to minimize data loss.
    - Exposes helpers to read events and fetch recent entries.
    """

    def __init__(self, path: str = "logs/events.jsonl"):
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

    def _validate_event(self, event: Dict) -> None:
        if not isinstance(event, dict):
            raise ValueError("event must be a dict")
        if "type" not in event:
            raise ValueError("event must include a 'type' field")

    def append_event(self, event: Dict, version: Optional[str] = "v1") -> Dict:
        self._validate_event(event)
        envelope = {
            "id": str(uuid.uuid4()),
            "timestamp": time.time(),
            "version": version,
            "event": event,
        }
        # Append and fsync to reduce risk of loss on crash.
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(envelope) + "\n")
            fh.flush()
            try:
                os.fsync(fh.fileno())
            except OSError:
                # Best-effort: not all environments support fsync on every fs
                pass
        return envelope

    def read_events(self) -> Generator[Dict, None, None]:
        if not os.path.exists(self.path):
            return
        with open(self.path, "r", encoding="utf-8") as fh:
            for line in fh:
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue

    def tail(self, n: int = 10) -> List[Dict]:
        """Return the last `n` events."""
        if not os.path.exists(self.path):
            return []
        with open(self.path, "r", encoding="utf-8") as fh:
            lines = fh.readlines()[-n:]
        out = []
        for l in lines:
            try:
                out.append(json.loads(l))
            except json.JSONDecodeError:
                continue
        return out
