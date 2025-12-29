# JARVIS — Modular Monolithic AI Operating Assistant

JARVIS is a safe, extensible AI Operating Assistant with a shadow-trained personal foundation model. This repository contains the core monolithic architecture, agents, orchestrator, perception, memory, and tooling to build the assistant.

License: MIT — see `LICENSE` for details.

## Quickstart (developer)

1. Create a virtualenv and activate it

   python3 -m venv .venv
   . .venv/bin/activate

2. Install dependencies

   pip install -r requirements.txt

3. Run tests

   make test

4. Run the demo (when available)

   make demo


Remote LLM integration

- To use OpenAI, set `OPENAI_API_KEY` in your environment; optionally set `OPENAI_API_BASE` if using a non-default endpoint.
- To use HuggingFace Inference API, set `HF_API_KEY` and optionally `HF_API_URL`.

Example (OpenAI):

    export OPENAI_API_KEY="sk-..."
    python main.py

Note: network calls will be made when using remote providers; in CI or tests, network calls are mocked. See `docs/remote_models.md` for details.

## Project structure
- `core/` — core orchestration logic and agent registry
- `orchestrator/` — brain: intent parser, task planner, router, execution manager
- `perception/` — sensors and event generation (voice, vision, system)
- `memory/` — short-term, long-term, episodic, and vector stores
- `shadow_learning/` — personal model training scaffolding
- `agents/` — modular single-responsibility agents
- `docs/` — architecture and design documents

For detailed roadmap and contribution guidelines, see `ROADMAP.md` and `CONTRIBUTING.md`.
