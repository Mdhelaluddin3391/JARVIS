import re
from typing import Dict, Any


class IntentParser:
    """Keyword + regex-based lightweight NLU for prototyping.

    Returns a dict with keys: intent, confidence, entities.
    This is a stopgap until a proper LLM-powered NLU is added.
    """

    KEYWORD_MAP = {
        "shutdown": "shutdown_system",
        "reboot": "reboot_system",
        "wifi": "manage_wifi",
        "open": "open_app",
        "search": "search_web",
        "play": "play_music",
        "music": "play_music",
    }

    APP_RE = re.compile(r"open\s+(?P<app>[a-z0-9_\-]+)", re.I)
    PLAY_RE = re.compile(r"play\s+(?P<query>.+)$", re.I)
    DEVICE_RE = re.compile(r"(wifi|bluetooth|screen|volume|battery)", re.I)
    NUMBER_RE = re.compile(r"(?P<num>\d+)")

    def parse(self, event: Dict[str, Any]) -> Dict[str, Any]:
        text = (event.get("text") or "").strip()
        lower = text.lower()

        # base confidence from perception
        confidence = float(event.get("confidence", 1.0))

        # intent detection by keyword
        intent = "unknown"
        for k, v in self.KEYWORD_MAP.items():
            if k in lower:
                intent = v
                break

        entities = {}
        m_app = self.APP_RE.search(text)
        if m_app:
            entities["app"] = m_app.group("app")

        m_play = self.PLAY_RE.search(text)
        if m_play:
            entities["query"] = m_play.group("query").strip()

        m_dev = self.DEVICE_RE.search(text)
        if m_dev:
            entities["device"] = m_dev.group(1).lower()

        m_num = self.NUMBER_RE.search(text)
        if m_num:
            entities["number"] = int(m_num.group("num"))

        # strengthen confidence if entities present
        if entities:
            confidence = min(0.99, confidence + 0.1)

        return {"intent": intent, "confidence": confidence, "entities": entities, "text": text}
