import asyncio
import os
import shutil
import subprocess
import tempfile
import threading
from typing import Optional


class BaseTTSEngine:
    """Abstract base for TTS engines."""

    def speak(self, text: str, block: bool = False) -> None:
        raise NotImplementedError


class DummyTTSEngine(BaseTTSEngine):
    def speak(self, text: str, block: bool = False) -> None:
        print(f"[TTS] {text}")


# Edge TTS engine (async-backed). Falls back to pyttsx3 if edge-tts isn't available.
class EdgeTTSEngine(BaseTTSEngine):
    def __init__(self, voice: Optional[str] = None):
        try:
            import edge_tts  # type: ignore
        except Exception as e:  # pragma: no cover - import failures handled in tests
            raise

        self.edge_tts = edge_tts
        self.voice = voice or "en-US-JennyNeural"

    async def _synthesize_to_file(self, text: str, outpath: str) -> None:
        comm = self.edge_tts.Communicate(text, voice=self.voice)
        # edge_tts provides a `save` coroutine that writes to a file
        await comm.save(outpath)

    def _play_file(self, filepath: str, block: bool = False) -> subprocess.Popen:
        # Prefer mpv/ffplay/vlc, else xdg-open
        for player in ("mpv", "ffplay", "vlc", "xdg-open"):
            path = shutil.which(player)
            if path:
                if player == "ffplay":
                    cmd = [path, "-nodisp", "-autoexit", filepath]
                elif player == "mpv":
                    cmd = [path, "--no-video", filepath]
                else:
                    cmd = [path, filepath]
                proc = subprocess.Popen(cmd)

                if block:
                    proc.wait()
                return proc

        # As a last resort, raise an error
        raise RuntimeError("No player found to play TTS audio")

    async def _stream_and_play(self, text: str, player_cmd: list, block: bool = False) -> None:
        # Start player that accepts piped audio on stdin
        proc = subprocess.Popen(player_cmd, stdin=subprocess.PIPE)

        try:
            comm = self.edge_tts.Communicate(text, voice=self.voice)
            # `stream()` yields messages with an `audio` attribute (bytes or base64 string)
            async for msg in comm.stream():
                audio = getattr(msg, "audio", None)
                if audio is None:
                    continue

                # If base64 str, decode
                if isinstance(audio, str):
                    try:
                        import base64

                        audio = base64.b64decode(audio)
                    except Exception:
                        # Not base64; skip
                        continue

                try:
                    proc.stdin.write(audio)
                    proc.stdin.flush()
                except BrokenPipeError:
                    break

            # Signal EOF and wait appropriately. For blocking calls, wait before closing stdin to avoid
            # IO on closed-buffer issues in test doubles.
            try:
                proc.stdin.flush()
            except Exception:
                pass

            if block:
                proc.wait()
                try:
                    proc.stdin.close()
                except Exception:
                    pass
            else:
                try:
                    proc.stdin.close()
                except Exception:
                    pass
        finally:
            # Ensure we don't leave process dangling for blocking calls
            if block:
                try:
                    proc.wait()
                except Exception:
                    pass

    def speak(self, text: str, block: bool = False, stream: bool = False) -> None:
        # If streaming requested, try to use a player that accepts stdin
        if stream:
            # Prefer ffplay or mpv (with stdin support)
            ffplay = shutil.which("ffplay")
            mpv = shutil.which("mpv")
            player_cmd = None
            if ffplay:
                player_cmd = [ffplay, "-nodisp", "-autoexit", "-i", "pipe:0"]
            elif mpv:
                player_cmd = [mpv, "--no-video", "--demuxer-lavf-format=mp3", "-"]

            if player_cmd is None:
                raise RuntimeError("No streaming-capable player found for EdgeTTSEngine")

            async def stream_and_play():
                await self._stream_and_play(text, player_cmd, block=block)

            # Run the async streaming in a fresh event loop
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():  # pragma: no cover - hard to reproduce in tests
                    thread = threading.Thread(target=lambda: asyncio.run(stream_and_play()), daemon=True)
                    thread.start()
                    return
            except RuntimeError:
                pass

            asyncio.run(stream_and_play())
            return

        # Fallback to file-based synthesis
        fd, path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)

        async def synth_and_play():
            try:
                await self._synthesize_to_file(text, path)

                # Start player
                proc = self._play_file(path, block=block)

                if not block:
                    # If non-blocking, clean up when process exits in background
                    def cleanup_when_done(p, file_path):
                        p.wait()
                        try:
                            os.remove(file_path)
                        except Exception:
                            pass

                    t = threading.Thread(target=cleanup_when_done, args=(proc, path), daemon=True)
                    t.start()
                else:
                    # blocking path should have removed file if player exited
                    try:
                        os.remove(path)
                    except Exception:
                        pass
            except Exception:
                # On failure, remove file if exists
                try:
                    if os.path.exists(path):
                        os.remove(path)
                except Exception:
                    pass
                raise

        # Run the async synthesis in a fresh event loop
        try:
            # If there's an active loop, create a new one in a thread
            loop = asyncio.get_event_loop()
            if loop.is_running():  # pragma: no cover - hard to reproduce in tests
                thread = threading.Thread(target=lambda: asyncio.run(synth_and_play()), daemon=True)
                thread.start()
                return
        except RuntimeError:
            # No running loop
            pass

        asyncio.run(synth_and_play())


# pyttsx3 fallback engine (synchronous behind the scenes)
class Pyttsx3TTSEngine(BaseTTSEngine):
    def __init__(self):
        try:
            import pyttsx3  # type: ignore
        except Exception as e:  # pragma: no cover
            raise

        self.pyttsx3 = pyttsx3
        self.engine = self.pyttsx3.init()

    def speak(self, text: str, block: bool = False) -> None:
        def run_speech():
            self.engine.say(text)
            self.engine.runAndWait()

        if block:
            run_speech()
        else:
            t = threading.Thread(target=run_speech, daemon=True)
            t.start()
