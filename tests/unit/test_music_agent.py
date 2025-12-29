import os
import subprocess
import types

from core.agents.safe.music_agent import MusicAgent


def test_music_agent_fallback(tmp_path, monkeypatch):
    agent = MusicAgent()
    # no music dir exists -> fallback
    res = agent.execute("play", {"query": "some song", "prefer_local": True})
    assert res["status"] == "fallback"


def test_music_agent_play_local(tmp_path, monkeypatch):
    # create a music dir with a file matching the query
    music_dir = tmp_path / "Music"
    music_dir.mkdir()
    song = music_dir / "my song.mp3"
    song.write_text("fake mp3 content")

    monkeypatch.setenv("MUSIC_DIR", str(music_dir))

    # monkeypatch Popen to a dummy that pretends to start
    class DummyP:
        def __init__(self, *a, **k):
            pass

        def terminate(self):
            pass

        def wait(self, timeout=None):
            pass

    monkeypatch.setattr(subprocess, "Popen", DummyP)

    agent = MusicAgent()
    res = agent.execute("play", {"query": "my song", "prefer_local": True})
    assert res["status"] == "playing"
    assert res["source"] == "local"
    assert "my song" in res["track"]
