import os
import subprocess
import tempfile
import types

import pytest


def test_pyttsx3_engine_calls_run(monkeypatch):
    called = {"say": False, "run": False}

    class DummyEngine:
        def say(self, text):
            called["say"] = True

        def runAndWait(self):
            called["run"] = True

    def fake_init():
        return DummyEngine()

    monkeypatch.setitem(__import__("sys").modules, "pyttsx3", types.SimpleNamespace(init=fake_init))

    from voice.tts_engine import Pyttsx3TTSEngine

    e = Pyttsx3TTSEngine()
    e.speak("hello world", block=True)

    assert called["say"]
    assert called["run"]


def test_edge_tts_synth_and_play_blocking(monkeypatch, tmp_path):
    # Monkeypatch the internal _synthesize_to_file coroutine to write a file
    synth_called = {"called": False}

    async def fake_synth(self, text, outpath):
        synth_called["called"] = True
        with open(outpath, "wb") as f:
            f.write(b"dummy mp3")

    monkeypatch.setattr("voice.tts_engine.EdgeTTSEngine._synthesize_to_file", fake_synth)

    # Force player selection to use a known player path
    monkeypatch.setattr("shutil.which", lambda p: "/usr/bin/mpv")

    # Monkeypatch subprocess.Popen so it doesn't actually run a player
    launched = {}

    class DummyProc:
        def __init__(self, cmd):
            launched["cmd"] = cmd

        def wait(self):
            return 0

    monkeypatch.setattr("subprocess.Popen", DummyProc)

    from voice.tts_engine import EdgeTTSEngine

    e = EdgeTTSEngine()
    # Use blocking speak: file should be removed after play
    e.speak("hello there", block=True)

    assert synth_called["called"]
    assert "mpv" in launched["cmd"][0]


def test_edge_tts_streaming_blocking(monkeypatch):
    # Fake the stream generator to yield a couple of audio chunks
    stream_called = {"called": False}

    async def fake_stream(self):
        stream_called["called"] = True

        class Msg:
            def __init__(self, audio):
                self.audio = audio

        yield Msg(b"chunk1")
        yield Msg(b"chunk2")

    class DummyComm:
        def __init__(self, text, voice=None):
            pass

        def stream(self):
            return fake_stream(self)

    import sys
    monkeypatch.setitem(sys.modules, "edge_tts", types.SimpleNamespace(Communicate=DummyComm))

    # Force stream-capable player
    monkeypatch.setattr("shutil.which", lambda p: "/usr/bin/ffplay")

    written = {"data": b"", "cmd": None}

    class DummyProc:
        def __init__(self, cmd, stdin=None, **kwargs):
            written["cmd"] = cmd
            import io

            # emulate a process with a writable stdin buffer but intercept writes
            self.stdin = types.SimpleNamespace()
            self._buf = bytearray()

            def write(data):
                # record data written
                self._buf.extend(data)

            def flush():
                pass

            def close():
                # closing should not prevent inspection in wait()
                pass

            self.stdin.write = write
            self.stdin.flush = flush
            self.stdin.close = close

        def wait(self):
            written["data"] = bytes(self._buf)
            return 0

    monkeypatch.setattr("subprocess.Popen", DummyProc)

    from voice.tts_engine import EdgeTTSEngine

    e = EdgeTTSEngine()

    # Sanity-check the Communicate was patched correctly
    assert hasattr(e, "edge_tts")
    assert getattr(e.edge_tts, "Communicate", None) is not None

    # Ensure the stream value is an async generator (so 'async for' will work)
    comm_inst = e.edge_tts.Communicate("x", voice=None)
    import inspect

    gen = comm_inst.stream()
    assert inspect.isasyncgen(gen)

    player_cmd = ["/usr/bin/ffplay", "-nodisp", "-autoexit", "-i", "pipe:0"]

    import asyncio

    asyncio.run(e._stream_and_play("hello stream", player_cmd, block=True))

    assert stream_called["called"]
    assert b"chunk1" in written["data"]
    assert b"chunk2" in written["data"]
    assert "ffplay" in written["cmd"][0]


def test_speaker_fallback_to_pyttsx3(monkeypatch):
    # Make EdgeTTSEngine raise during init
    class BadEdge:
        def __init__(self):
            raise RuntimeError("no edge")

    monkeypatch.setattr("voice.tts_engine.EdgeTTSEngine", BadEdge, raising=True)

    # Provide a fake pyttsx3 module
    class DummyEngine:
        def say(self, text):
            pass

        def runAndWait(self):
            pass

    monkeypatch.setitem(__import__("sys").modules, "pyttsx3", types.SimpleNamespace(init=lambda: DummyEngine()))

    from voice.speaker import Speaker
    from voice.tts_engine import Pyttsx3TTSEngine

    s = Speaker()
    assert isinstance(s.engine, Pyttsx3TTSEngine)
