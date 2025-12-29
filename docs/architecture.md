# JARVIS Architecture

A Modular Monolithic AI Operating Assistant with a Personal Foundation Model.

## Overview
JARVIS is designed to be a safe, extensible, and future-proof assistant that interacts with the OS, applications, and network while maintaining strict control boundaries. The golden rule: LLMs never directly control the system—only agents can execute actions.

High-level flow:

User / Voice / UI → Perception Layer → Orchestrator (Brain) → Agent Layer → System / OS / Network → Memory + Audit → Event Bus (Read Only) → Shadow Learning

## Layers

### Perception Layer
- Responsibility: Convert real-world inputs to structured, privacy-safe events.
- Inputs: Voice (wake word, speech), Screen/vision, Keyboard/mouse, System sensors
- Output: Events (typed, versioned JSON), e.g. `{ "type":"VOICE_COMMAND", "text":"wifi band karo", "confidence": 0.94 }`
- Raw audio/video never reaches an LLM.

### Orchestrator (Brain)
- Responsibilities: intent detection, task planning, agent routing, execution supervision, feedback aggregation.
- Subcomponents: Intent Parser, Task Planner (LLM orchestration), Router, Execution Manager
- LLM Selection Policy: local 7B for simple tasks; remote 70B for deep reasoning; policy engine rejects unsafe intents.

### Agent Layer
- Agents: single-responsibility executors (wifi_agent, power_agent, file_agent, browser_agent)
- Metadata: risk level, required permissions, sandbox profile
- Workflow example: user says "Shutdown system" → power_agent (high risk) → permission checks → user confirmation → execute

### Permissions & Policy Engine
- Agent-level authorization, user-based access, contextual validation
- Policy examples: time-based rules, battery/network constraints, voice recognition trust

### Memory System
- Types: short-term, long-term, episodic, semantic, vector
- Access: orchestrator has runtime access; shadow learner read-only and filtered

### Event Bus
- Purpose: immutable, versioned log of actions and decisions
- Rules: append-only, versioned schemas, read-only to learners

### Shadow Learning
- Role: personal foundation model trained from observed behavior (teacher-student style)
- Restrictions: read-only access to logs, no system control, no automatic deployment

## Training Pipeline
Raw Events → Filtering & PII removal → Processed Datasets → Pretraining → Fine-tuning (LoRA) → RLHF → Evaluation → Model Registry

Governance: explicit user consent, retention policies, full audit logs

## Security, Failure, and Audit
- Security: sandbox profiles, secrets manager, intrusion detection
- Failure handling: chaos testing, automatic recovery, observability
- Audit: append-only logs, explainable decisions, human override

## Roadmap & Priorities
- Phase 0: project scaffolding, dev tooling, CI
- Phase 1: core infra (Perception, Orchestrator, Agents, Event Bus)
- Phase 2: LLM integration and safety tooling
- Phase 3: Shadow learning pipelines and evaluation

---

For implementation details, see `ROADMAP.md` and `CONTRIBUTING.md`. Add design proposals to `docs/` and link them from this page.
