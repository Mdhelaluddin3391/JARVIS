Remote LLM integration

This project supports remote LLM providers via `llm_runtime/manager.RemoteAdapter`.

Providers supported:

- OpenAI (Chat Completions API)
- HuggingFace Inference API

Environment variables:

- `OPENAI_API_KEY` - if set, `RemoteAdapter` will use the OpenAI Chat Completions API.
- `OPENAI_API_BASE` - optional, to use an alternate OpenAI-compatible base URL.
- `HF_API_KEY` - if set, `RemoteAdapter` can call the HuggingFace Inference API.
- `HF_API_URL` - optional custom HF inference base URL.
- `LLM_PROVIDER` - can be set to `openai` or `hf` to force a provider.

Notes:
- Network calls are made using `requests` (the library is optional for running tests because tests mock network calls).
- Take care not to send sensitive data to remote providers; the architecture enforces that LLMs do not directly execute system commands — only agents can take actions.

Example usage:

    from llm_runtime.manager import RemoteAdapter

    a = RemoteAdapter(model_name="gpt-4", provider="openai", api_key="<key>")
    print(a.generate("Say hello"))
