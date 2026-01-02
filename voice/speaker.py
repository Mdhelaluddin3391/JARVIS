from typing import Optional

from voice.tts_engine import BaseTTSEngine, DummyTTSEngine


class Speaker:
    def __init__(self, engine: Optional[BaseTTSEngine] = None):
        if engine is not None:
            self.engine = engine
            return

        # Try preferred engines in order: EdgeTTSEngine, Pyttsx3TTSEngine, Dummy
        try:
            from voice.tts_engine import EdgeTTSEngine

            try:
                self.engine = EdgeTTSEngine()
                return
            except Exception:
                pass
        except Exception:
            pass

        try:
            from voice.tts_engine import Pyttsx3TTSEngine

            try:
                self.engine = Pyttsx3TTSEngine()
                return
            except Exception:
                pass
        except Exception:
            pass

        self.engine = DummyTTSEngine()

    def speak(self, text: str, block: bool = False) -> None:
        self.engine.speak(text, block=block)
