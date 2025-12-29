import json
import os
import time
from typing import Callable, Dict, List


class PerceptionManager:
    """Simple perception manager that emits structured events and notifies listeners.

    Listeners receive a dict event object.
    """

    def __init__(self):
        self._listeners: List[Callable[[Dict], None]] = []

    def register_listener(self, cb: Callable[[Dict], None]) -> None:
        self._listeners.append(cb)

    def emit_event(self, event: Dict) -> None:
        event.setdefault("timestamp", time.time())
        for cb in list(self._listeners):
            try:
                cb(event)
            except Exception:
                # Keep perception resilient; listeners must handle errors
                continue

    def emit_voice_event(self, text: str, confidence: float = 1.0) -> None:
        event = {
            "type": "VOICE_COMMAND",
            "text": text,
            "confidence": float(confidence),
        }
        self.emit_event(event)
