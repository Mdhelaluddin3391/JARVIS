# JARVIS Roadmap

This document outlines a suggested roadmap and milestones to implement the JARVIS architecture.

## Vision
Build a safe, modular AI Operating Assistant with a personal foundation model, starting with a secure, extensible modular monolith and an MVP voice-driven demo.

## Phases

### Phase 0 — Project Setup (Current)
- Project scaffolding: docs, contributing, CI, Makefile, basic dev tooling ✅
- Define milestones and acceptance criteria

### Phase 1 — Core Infrastructure (MVP)
- Perception layer basics (voice -> event pipeline)
- Orchestrator skeleton (Intent Parser, Task Planner, Router)
- Agent registry and sample agents (wifi, power, file)
- Permission & policy engine prototype
- Append-only Event Bus with versioned schemas
- Unit tests & CI

### Phase 2 — LLM Integration & Safety
- LLM adapter interfaces and selection policy (local vs server)
- Local model runner for offline tasks (7B stub)
- Fine-grained sandboxing for agents
- Explainability & audit hooks

### Phase 3 — Shadow Learning & Personal LLM
- Event dataset extraction with PII filtering
- Offline training pipeline (pretrain, LoRA, RLHF scaffolding)
- Evaluation and model registry

### Phase 4 — Maturity & Ecosystem
- External SDK & secure API exposure (read-only/limited write)
- Advisor mode and optional low-risk agent automation
- Packaging, distribution, and documentation for end-users

## Goals & Success Criteria
- Safety-first: policy checks block unsafe operations by default
- Auditable: all decisions and actions are logged in an append-only store
- Extensible: adding a new agent requires minimal boilerplate
- Reproducible: tests and CI govern code quality

---

*Next step:* begin Phase 0 tasks and scaffold the project (docs, CI, dev tooling).