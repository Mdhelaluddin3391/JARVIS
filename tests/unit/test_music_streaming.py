from core.agents.safe.music_agent import MusicAgent
from integrations.streaming.youtube_provider import YouTubeProvider


def test_music_agent_streams_on_no_local(tmp_path):
    m = MusicAgent(music_dir=str(tmp_path / "empty"), )
    res = m.execute("play", {"query": "jazz", "prefer_local": True})
    assert res["status"] in ("fallback", "playing")


def test_youtube_provider():
    url = YouTubeProvider.search_play_url("lofi beats")
    assert "youtube.com" in url
