# JARVIS Demo

This demo shows a minimal end-to-end flow from a "voice" input (text typed in CLI) through the Perception layer to the Orchestrator and Agent execution.

Run the demo:

    make demo

Or run directly:

    . .venv/bin/activate
    python main.py

Type a short command like `wifi toggle` and observe the log, or `exit` to quit.

Notes on new routing and confirmation behavior:

- The system now includes a `Router` that inspects parsed intents and decides whether to execute a plan or request user confirmation for high-risk actions.
- Examples:
  - `wifi toggle` → routes to `wifi_agent` and executes immediately (multi-step: toggle then network status check).
  - `shutdown system` with low confidence → prompts for confirmation before execution (CLI will ask yes/no and execute on confirm).
- Routing policies:
  - **Agent prioritization:** tasks are ordered by agent `priority` metadata. Register an agent with a higher `priority` attribute to prefer its tasks when multiple tasks exist.
  - **Routing preferences:** pass `context["prefer_agent"]` to bias the router to move that agent's task to the front of the plan.
  - **Approvals (persistent):** you can grant persistent approvals for an `agent:action` which will bypass confirmation for that action until expiry. Use the CLI confirmation flow and choose to remember the decision for N hours.

This demo is still a prototype and should not run privileged actions without confirmation in a real environment.
