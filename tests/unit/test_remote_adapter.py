import types

import llm_runtime.manager as mgr


class DummyResponse:
    def __init__(self, data):
        self._data = data

    def json(self):
        return self._data

    def raise_for_status(self):
        return None


def test_openai_generate(monkeypatch):
    captured = {}

    def fake_post(url, headers=None, json=None, timeout=None):
        captured['url'] = url
        captured['headers'] = headers
        captured['json'] = json
        return DummyResponse({"choices": [{"message": {"content": "OpenAI says hi"}}]})

    # ensure requests exists but is controlled
    monkeypatch.setattr(mgr, "requests", types.SimpleNamespace(post=fake_post))

    a = mgr.RemoteAdapter(model_name="gpt-test", provider="openai", api_key="k")
    res = a.generate("hello")
    assert res == "OpenAI says hi"
    assert "openai" in captured['url'] or "chat" in captured['url']


def test_hf_generate(monkeypatch):
    captured = {}

    def fake_post(url, headers=None, json=None, timeout=None):
        captured['url'] = url
        captured['headers'] = headers
        captured['json'] = json
        return DummyResponse([{"generated_text": "HF reply"}])

    monkeypatch.setattr(mgr, "requests", types.SimpleNamespace(post=fake_post))

    a = mgr.RemoteAdapter(model_name="hf-model", provider="hf", api_key="k")
    res = a.generate("hey")
    assert res == "HF reply"
    assert "huggingface" in captured['url'] or "/models/" in captured['url']
