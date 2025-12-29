from typing import Optional


class BaseSTTEngine:
    def transcribe(self, audio: Optional[bytes] = None) -> str:
        raise NotImplementedError


class DummySTTEngine(BaseSTTEngine):
    """Simple STT engine for demo/testing that returns provided text input.

    For real usage, implement wrapper for whisper/vosk or another STT system.
    """

    def transcribe(self, audio: Optional[bytes] = None) -> str:
        # In the demo, `audio` will be interpreted as UTF-8 bytes for direct text input
        if audio is None:
            return ""
        try:
            return audio.decode("utf-8")
        except Exception:
            return ""
