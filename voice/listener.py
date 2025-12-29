from typing import Optional
from voice.stt_engine import BaseSTTEngine, DummySTTEngine


class Listener:
    def __init__(self, engine: Optional[BaseSTTEngine] = None):
        self.engine = engine or DummySTTEngine()

    def listen_from_text(self, text: str) -> str:
        # Demo helper: treat text as UTF-8 bytes for DummySTT
        return self.engine.transcribe(text.encode("utf-8"))

    def listen(self, timeout: int = 5) -> str:
        """Simple blocking listen for demo: read one line from stdin or return empty string.

        In production, replace with streaming STT that honors timeout.
        """
        try:
            return input().strip()
        except Exception:
            return ""
