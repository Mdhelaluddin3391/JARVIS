from typing import Optional

try:
    import speech_recognition as sr
except Exception:
    sr = None


class BaseSTTEngine:
    def transcribe(self, audio: Optional[bytes] = None) -> str:
        raise NotImplementedError


class DummySTTEngine(BaseSTTEngine):
    """Simple STT engine for demo/testing that returns provided text input.

    Kept for unit tests and environments where real STT isn't available.
    """

    def transcribe(self, audio: Optional[bytes] = None) -> str:
        if audio is None:
            return ""
        try:
            if isinstance(audio, (bytes, bytearray)):
                return audio.decode("utf-8")
            return str(audio)
        except Exception:
            return ""


class SpeechRecognitionSTTEngine(BaseSTTEngine):
    """SpeechRecognition-based STT engine.

    - Uses the `speech_recognition` library to listen to microphone and transcribe speech.
    - For production, consider configuring alternative backends (Google, Sphinx, etc.).
    - This class raises a RuntimeError if `speech_recognition` is not installed.
    """

    def __init__(self, mic_index: Optional[int] = None, timeout: int = 5, phrase_time_limit: Optional[int] = None):
        if sr is None:
            raise RuntimeError("speech_recognition package is required for SpeechRecognitionSTTEngine")
        self.recognizer = sr.Recognizer()
        self.mic_index = mic_index
        self.timeout = timeout
        self.phrase_time_limit = phrase_time_limit

    def listen_once(self) -> str:
        """Listen once from the default microphone and return transcribed text.

        This is a blocking call suitable for demo/CLI usage. For production, implement async/streaming.
        """
        with sr.Microphone(device_index=self.mic_index) as source:
            try:
                # optional ambient noise adjustment
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            except Exception:
                pass
            audio = self.recognizer.listen(source, timeout=self.timeout, phrase_time_limit=self.phrase_time_limit)
        try:
            # Default to Google recognizer; in production you may switch to a different recognizer
            return self.recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            # network / service error
            return ""

    def transcribe(self, audio: Optional[bytes] = None) -> str:
        # If raw bytes that are actually text have been passed (testing), decode them
        if audio is None:
            return ""
        if isinstance(audio, (bytes, bytearray)):
            try:
                return audio.decode("utf-8")
            except Exception:
                return ""
        return str(audio)
