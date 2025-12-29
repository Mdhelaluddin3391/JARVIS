from orchestrator.intent_parser import IntentParser


def test_play_music_parsing():
    p = IntentParser()
    parsed = p.parse({"text": "Hi Jarvis, play Bohemian Rhapsody", "confidence": 0.95})
    assert parsed["intent"] == "play_music"
    assert "query" in parsed["entities"]
    assert "bohemian" in parsed["entities"]["query"].lower()
