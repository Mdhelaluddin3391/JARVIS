from voice.stt_engine import DummySTTEngine
from voice.tts_engine import DummyTTSEngine


def test_dummy_stt_transcribe():
    s = DummySTTEngine()
    assert s.transcribe(b"hello") == "hello"


def test_dummy_tts_prints(capfd):
    t = DummyTTSEngine()
    t.speak("hi there")
    out = capfd.readouterr().out
    assert "[TTS] hi there" in out
