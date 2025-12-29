from typing import Optional
from voice.tts_engine import BaseTTSEngine, DummyTTSEngine


class Speaker:
    def __init__(self, engine: Optional[BaseTTSEngine] = None):
        self.engine = engine or DummyTTSEngine()

    def speak(self, text: str) -> None:
        self.engine.speak(text)
