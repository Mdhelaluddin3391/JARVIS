import types

import llm_runtime.manager as mgr


class DummyResponse:
    def __init__(self, data):
        self._data = data

    def json(self):
        return self._data

    def raise_for_status(self):
        return None


def test_local_http_adapter(monkeypatch):
    captured = {}

    def fake_post(url, json=None, timeout=None):
        captured['url'] = url
        captured['json'] = json
        return DummyResponse([{"generated_text": "local answer"}])

    monkeypatch.setattr(mgr, "requests", types.SimpleNamespace(post=fake_post))

    a = mgr.LocalHTTPAdapter(model_name="local-7b", url="http://localhost:8080/generate")
    r = a.generate("hello")
    assert r == "local answer"
    assert "localhost" in captured['url']


def test_local_subprocess_adapter(tmp_path):
    # create a tiny script that echoes stdin to stdout
    script = tmp_path / "echo.sh"
    script.write_text("#!/bin/sh\ncat -")
    script.chmod(0o755)

    a = mgr.LocalSubprocessAdapter(cmd=[str(script)])
    res = a.generate("ping")
    assert res == "ping"
