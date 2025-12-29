import os
import json
from typing import Any, Dict

try:
    import requests
except Exception:  # pragma: no cover - tests will mock network calls
    requests = None


class BaseAdapter:
    def generate(self, prompt: str, **kwargs) -> str:
        raise NotImplementedError


class LocalAdapter(BaseAdapter):
    def __init__(self, model_name: str = "local-7b"):
        self.model_name = model_name

    def generate(self, prompt: str, **kwargs) -> str:
        # Placeholder: integrate real local model runner
        return f"[local:{self.model_name}] {prompt}"


class LocalHTTPAdapter(BaseAdapter):
    """Adapter that sends prompts to a local LLM HTTP server (e.g., text-generation-webui, local FastAPI).

    Configure with `LOCAL_LLM_URL` env var (e.g., http://localhost:5000/generate) and model via `model_name`.
    The adapter POSTs a JSON payload {"inputs": prompt, "parameters": {...}} and extracts text from the response.
    """

    def __init__(self, model_name: str = "local-7b", url: str | None = None):
        self.model_name = model_name
        self.url = url or os.getenv("LOCAL_LLM_URL") or f"http://localhost:8080/models/{self.model_name}/generate"

    def _assert_requests(self):
        if requests is None:
            raise RuntimeError("LocalHTTPAdapter requires 'requests' to be installed")

    def generate(self, prompt: str, max_tokens: int = 128, temperature: float = 0.0, **kwargs) -> str:
        self._assert_requests()
        payload = {"inputs": prompt, "parameters": {"max_new_tokens": max_tokens, "temperature": temperature}}
        r = requests.post(self.url, json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()
        # Support common shapes returned by local servers
        if isinstance(data, dict) and "generated_text" in data:
            return data["generated_text"]
        if isinstance(data, list) and data and isinstance(data[0], dict) and "generated_text" in data[0]:
            return data[0]["generated_text"]
        if isinstance(data, dict) and "outputs" in data and isinstance(data["outputs"], list):
            out = data["outputs"][0]
            if isinstance(out, dict) and "text" in out:
                return out["text"]
        return json.dumps(data)


class LocalSubprocessAdapter(BaseAdapter):
    """Adapter that runs a local model runner via subprocess.

    The `cmd` should be a list of command parts to execute, where the prompt will be provided on stdin.
    For example: ['./run_local_model.sh']
    """

    def __init__(self, model_name: str = "local-7b", cmd: list | None = None):
        self.model_name = model_name
        self.cmd = cmd

    def generate(self, prompt: str, max_tokens: int = 128, temperature: float = 0.0, **kwargs) -> str:
        import subprocess

        if not self.cmd:
            raise RuntimeError("No command configured for LocalSubprocessAdapter")
        proc = subprocess.run(self.cmd, input=prompt.encode("utf-8"), capture_output=True, timeout=120)
        if proc.returncode != 0:
            raise RuntimeError(f"Local model failed: {proc.stderr.decode('utf-8')}")
        return proc.stdout.decode("utf-8").strip()


class RemoteAdapter(BaseAdapter):
    """Generic remote LLM adapter with support for OpenAI and HuggingFace Inference API.

    Selection of provider happens via environment variables:
    - If OPENAI_API_KEY is set -> use OpenAI Chat Completions endpoint
    - Else if HF_API_KEY is set -> use HuggingFace Inference API

    For tests we keep network calls testable by mocking `requests.post`.
    """

    def __init__(self, model_name: str = "gpt-4", provider: str | None = None, api_key: str | None = None, base_url: str | None = None):
        self.model_name = model_name
        self.provider = provider or os.getenv("LLM_PROVIDER")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("HF_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_API_BASE") or os.getenv("HF_API_URL")

        # auto-detect provider if not explicitly set
        if self.provider is None:
            if os.getenv("OPENAI_API_KEY"):
                self.provider = "openai"
            elif os.getenv("HF_API_KEY"):
                self.provider = "hf"
            else:
                # default to 'openai' for convenience (but will raise if no key)
                self.provider = "openai"

    def _assert_requests(self):
        if requests is None:
            raise RuntimeError("RemoteAdapter requires the 'requests' package to be installed")

    def generate(self, prompt: str, max_tokens: int = 128, temperature: float = 0.0, **kwargs) -> str:
        self._assert_requests()
        if self.provider == "openai":
            return self._generate_openai(prompt, max_tokens=max_tokens, temperature=temperature, **kwargs)
        elif self.provider == "hf" or self.provider == "huggingface":
            return self._generate_hf(prompt, max_tokens=max_tokens, temperature=temperature, **kwargs)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def _generate_openai(self, prompt: str, max_tokens: int = 128, temperature: float = 0.0, **kwargs) -> str:
        url = (self.base_url or "https://api.openai.com") + "/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        r = requests.post(url, headers=headers, json=payload, timeout=15)
        r.raise_for_status()
        data = r.json()
        # Support both 'choices[0].message.content' (chat) and 'choices[0].text' (completion)
        choice = data.get("choices", [{}])[0]
        if "message" in choice and choice["message"]:
            return choice["message"].get("content", "")
        return choice.get("text", "")

    def _generate_hf(self, prompt: str, max_tokens: int = 128, temperature: float = 0.0, **kwargs) -> str:
        model = self.model_name
        url = self.base_url or f"https://api-inference.huggingface.co/models/{model}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"inputs": prompt, "parameters": {"max_new_tokens": max_tokens, "temperature": temperature}}
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()
        # The HF inference API may return a string or a list/dict with generated_text
        if isinstance(data, str):
            return data
        if isinstance(data, list) and data and isinstance(data[0], dict) and "generated_text" in data[0]:
            return data[0]["generated_text"]
        if isinstance(data, dict) and "generated_text" in data:
            return data["generated_text"]
        # Fallback: stringify
        return json.dumps(data)


class LLMSelector:
    """Selects LLM adapter based on simple heuristic: task complexity or forced preference."""

    def __init__(self, local: BaseAdapter, remote: BaseAdapter):
        self.local = local
        self.remote = remote

    def select(self, *, text: str = "", complexity_hint: int = 0, prefer: str = None) -> BaseAdapter:
        if prefer == "local":
            return self.local
        if prefer == "remote":
            return self.remote
        # basic heuristic: long text or high complexity hint -> remote
        if complexity_hint >= 2 or len(text) > 200:
            return self.remote
        return self.local
