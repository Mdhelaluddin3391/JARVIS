from orchestrator.intent_parser import IntentParser


def test_wifi_toggle_parsing():
    p = IntentParser()
    parsed = p.parse({"text": "wifi toggle", "confidence": 0.9})
    assert parsed["intent"] == "manage_wifi"
    assert parsed["entities"].get("device") == "wifi"
    assert parsed["confidence"] > 0.9


def test_open_app_parsing():
    p = IntentParser()
    parsed = p.parse({"text": "Open Chrome", "confidence": 0.8})
    assert parsed["intent"] == "open_app"
    assert parsed["entities"].get("app") == "Chrome" or parsed["entities"].get("app") == "chrome"


def test_unknown_intent():
    p = IntentParser()
    parsed = p.parse({"text": "foobar something", "confidence": 0.5})
    assert parsed["intent"] == "unknown"
    assert parsed["confidence"] == 0.5
