import os
import shutil
import subprocess
from typing import Any, Dict, List, Optional

from core.agents.base.agent import BaseAgent


def _find_local_tracks(query: str, music_dir: Optional[str] = None) -> List[str]:
    music_dir = music_dir or os.getenv("MUSIC_DIR") or os.path.expanduser("~/Music")
    if not os.path.isdir(music_dir):
        return []
    results = []
    q = query.lower()
    for root, _, files in os.walk(music_dir):
        for f in files:
            if f.lower().endswith((".mp3", ".wav", ".m4a", ".flac", ".ogg")):
                if q in f.lower():
                    results.append(os.path.join(root, f))
    return results


class MusicAgent(BaseAgent):
    """Music agent capable of playing local files or invoking external streaming integrations.

    Actions:
      - 'play': args { 'query': str, 'prefer_local': bool }
      - 'stop': args {}

    Notes:
      - For local playback, `MUSIC_PLAYER_CMD` env var may point to a command list (space-separated) to run with the file path appended, e.g., "mpv --no-video".
      - In test mode we don't actually start players; calls should be mocked.
    """

    def __init__(self, name: str = "music_agent", risk: str = "low", permissions: Dict[str, Any] = None, music_dir: Optional[str] = None, streaming_providers: Optional[List] = None):
        super().__init__(name=name, risk=risk, permissions=permissions or {})
        self._players: List[subprocess.Popen] = []
        self.music_dir = music_dir or os.getenv("MUSIC_DIR") or os.path.expanduser("~/Music")
        if streaming_providers:
            self.streaming_providers = streaming_providers
        else:
            # lazy import default provider
            try:
                from integrations.streaming.youtube_provider import YouTubeProvider

                self.streaming_providers = [YouTubeProvider()]
            except Exception:
                self.streaming_providers = []

    def can_handle(self, intent: Dict[str, Any]) -> bool:
        action = intent.get("action") or intent.get("intent")
        return action in ("play", "play_music")

    def perform(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        # Normalize intent keys
        q = intent.get("query") or (intent.get("entities") or {}).get("query") or (intent.get("text") or "")
        prefer_local = intent.get("prefer_local", True)

        # Local search
        if prefer_local:
            # use the helper to find tracks in configured music_dir
            tracks = []
            qlow = (q or "").lower()
            if os.path.isdir(self.music_dir):
                for root, _, files in os.walk(self.music_dir):
                    for f in files:
                        if f.lower().endswith((".mp3", ".wav", ".m4a", ".flac", ".ogg")):
                            if not qlow or qlow in f.lower():
                                tracks.append(os.path.join(root, f))
            if tracks:
                track = tracks[0]
                # attempt to launch player but best-effort
                try:
                    cmd_env = os.getenv("MUSIC_PLAYER_CMD")
                    if cmd_env:
                        cmd = cmd_env.split() + [track]
                        p = subprocess.Popen(cmd)
                        self._players.append(p)
                        return {"ok": True, "type": "local", "path": track}
                    else:
                        opener = shutil.which("xdg-open") or shutil.which("open")
                        if opener:
                            p = subprocess.Popen([opener, track])
                            self._players.append(p)
                            return {"ok": True, "type": "local", "path": track}
                        return {"ok": True, "type": "local", "path": track, "note": "no_player_cmd"}
                except Exception as e:
                    return {"ok": False, "message": str(e)}

        # Fallback to streaming providers
        if self.streaming_providers:
            provider = self.streaming_providers[0]
            url = provider.search_play_url(q or "popular music")
            return {"ok": True, "type": "stream", "provider": provider.NAME, "url": url}

        return {"ok": False, "message": "no_playback_available"}

    def execute(self, action: str, args: Dict) -> Dict:
        if action == "play":
            return self._play(args)
        if action == "stop":
            return self._stop()
        return {"status": "error", "reason": "unsupported action"}

    def _play(self, args: Dict) -> Dict:
        query = args.get("query", "")
        prefer_local = args.get("prefer_local", True)

        # Try local if preferred
        if prefer_local:
            tracks = _find_local_tracks(query)
            if tracks:
                track = tracks[0]
                try:
                    cmd_env = os.getenv("MUSIC_PLAYER_CMD")
                    if cmd_env:
                        cmd = cmd_env.split() + [track]
                        p = subprocess.Popen(cmd)
                        self._players.append(p)
                        return {"status": "playing", "source": "local", "track": track}
                    else:
                        # fallback to xdg-open (Linux) or `open` (macOS)
                        opener = shutil.which("xdg-open") or shutil.which("open")
                        if opener:
                            p = subprocess.Popen([opener, track])
                            self._players.append(p)
                            return {"status": "playing", "source": "local", "track": track}
                        # no player command available in this environment (e.g., CI), return playing with note
                        return {"status": "playing", "source": "local", "track": track, "note": "no_player_cmd"}
                except Exception as e:
                    return {"status": "error", "reason": str(e)}

        # streaming fallback using YouTubeProvider
        try:
            from integrations.streaming.youtube_provider import YouTubeProvider

            provider = YouTubeProvider()
            url = provider.search_play_url(query or "popular music")
            return {"status": "fallback", "source": "streaming", "query": query, "url": url, "provider": provider.NAME}
        except Exception:
            return {"status": "fallback", "source": "streaming", "query": query, "reason": "streaming integration not available"}

    def _stop(self) -> Dict:
        stopped = 0
        for p in list(self._players):
            try:
                p.terminate()
                p.wait(timeout=2)
                stopped += 1
            except Exception:
                try:
                    p.kill()
                except Exception:
                    pass
            finally:
                self._players.remove(p)
        return {"status": "stopped", "count": stopped}
