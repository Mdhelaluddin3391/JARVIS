from typing import Any, Dict

from core.agents.base.agent import BaseAgent
from llm_runtime.manager import LocalAdapter, RemoteAdapter, LLMSelector


class LLMAgent(BaseAgent):
    """Agent that queries an LLM and returns a textual answer.

    Usage: agent.execute('ask', {'prompt': '...','prefer': 'remote'|'local', 'complexity_hint': 0})
    """

    def __init__(self, name: str = "llm-agent", risk: str = "low", permissions: Dict[str, Any] = None, selector: LLMSelector | None = None):
        super().__init__(name=name, risk=risk, permissions=permissions or {})
        if selector is None:
            local = LocalAdapter()
            remote = RemoteAdapter()
            selector = LLMSelector(local=local, remote=remote)
        self.selector = selector

    def execute(self, action: str, args: Dict) -> Dict:
        if action != "ask":
            return {"status": "error", "reason": "unsupported action"}
        prompt = args.get("prompt", "")
        prefer = args.get("prefer")
        complexity_hint = args.get("complexity_hint", 0)
        adapter = self.selector.select(text=prompt, complexity_hint=complexity_hint, prefer=prefer)
        try:
            out = adapter.generate(prompt)
            return {"status": "ok", "response": out}
        except Exception as e:
            return {"status": "error", "reason": str(e)}
