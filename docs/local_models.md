# Running Local Models (Developer Notes)

This project includes a lightweight LLM adapter in `llm_runtime/manager.py`.
For development you can use the `LocalAdapter` stub; to run a real local model:

1. Pick a local runtime (e.g., `llama.cpp`, `ggml`, or a native PyTorch model).
2. Implement a concrete adapter that subclasses `BaseAdapter` in `llm_runtime/manager.py`.
   - Implement `generate(prompt, **kwargs)` to call the local runtime.
   - Ensure the adapter is non-blocking or add timeouts for long-running calls.
3. Keep model files outside the repository (add to `.gitignore`) and load from a configured path.

Security and privacy:
- Do not store or log secrets in plain text.
- Restrict model file access and consider sandboxing heavy-weight runtimes.

See `llm_runtime/manager.py` for the current interfaces and stubs.
