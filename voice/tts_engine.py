from typing import Optional


class BaseTTSEngine:
    def speak(self, text: str) -> None:
        raise NotImplementedError


class DummyTTSEngine(BaseTTSEngine):
    """Demo TTS that prints to stdout. For real TTS, implement wrappers over pyttsx3, TTS, or cloud TTS services."""

    def speak(self, text: str) -> None:
        print(f"TTS -> {text}")
