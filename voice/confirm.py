from typing import Optional

from voice.listener import Listener
from voice.speaker import Speaker


class VoiceApprover:
    """Ask a yes/no question over TTS and STT via Speaker and Listener.

    The `listener` must implement `listen(timeout: int) -> str` for interactive mode. For tests, pass a dummy listener.
    """

    def __init__(self, listener: Optional[Listener] = None, speaker: Optional[Speaker] = None):
        self.listener = listener or Listener()
        self.speaker = speaker or Speaker()

    def __call__(self, message: str) -> bool:
        try:
            self.speaker.speak(message)
        except Exception:
            pass
        # In demo, Listener.listen will read from input() or return an empty string
        resp = getattr(self.listener, "listen", lambda timeout=5: "")()
        if not resp:
            return False
        text = resp.lower().strip()
        return any(w in text for w in ("yes", "yeah", "y", "confirm", "ok", "sure"))
