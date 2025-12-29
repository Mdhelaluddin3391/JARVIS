from core.agents.safe.llm_agent import LLMAgent


class DummyAdapter:
    def __init__(self, text):
        self.text = text

    def generate(self, prompt: str, **kwargs):
        return self.text


class DummySelector:
    def __init__(self, adapter):
        self.adapter = adapter

    def select(self, **kwargs):
        return self.adapter


def test_llm_agent_ask_local_pref():
    adapter = DummyAdapter("local answer")
    sel = DummySelector(adapter)
    agent = LLMAgent(selector=sel)
    r = agent.execute("ask", {"prompt": "q", "prefer": "local"})
    assert r["status"] == "ok"
    assert r["response"] == "local answer"


def test_llm_agent_unsupported_action():
    agent = LLMAgent()
    r = agent.execute("foo", {})
    assert r["status"] == "error"
