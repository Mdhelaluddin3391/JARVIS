from typing import Callable, Dict, Any


def handle_confirmation(parsed_intent: Dict[str, Any], router, exec_mgr, context: Dict[str, Any] = None, input_fn: Callable[[str], str] = input) -> Dict:
    """Handle require_confirmation flows.

    - If the router indicates confirmation is required, prompt the user using input_fn.
    - If user confirms, re-run routing with user_confirmed=True and execute the resulting plan.

    Returns a dict describing the outcome: {status: 'confirmed'|'denied'|'no_confirmation_required'|'error', ...}
    """
    ctx = dict(context or {})

    route_res = router.route(parsed_intent, ctx)
    if route_res.get("status") != "require_confirmation":
        return {"status": "no_confirmation_required", "route": route_res}

    prompt = f"Confirm action '{parsed_intent.get('intent')}'? (y/n): "
    try:
        reply = input_fn(prompt).strip().lower()
    except Exception:
        return {"status": "error", "reason": "input_failed"}

    if reply in ("y", "yes"):
        # Optionally remember the decision for a TTL
        try:
            remember = input_fn("Remember this decision and auto-approve for N hours? Enter hours (0 for no): ").strip()
        except Exception:
            remember = "0"

        try:
            hours = int(remember) if remember else 0
        except ValueError:
            hours = 0

        if hours > 0:
            # Lazy import to avoid cycles
            from permissions.approvals import ApprovalStore

            store = ApprovalStore()
            # grant for agent/action according to the first task in plan
            first_task = route_res.get("needed")
            # route_res.needed contains 'intent' and 'confidence' only; identify agent/action by re-routing with confirmation
            r2 = router.route(parsed_intent, dict(ctx, user_confirmed=True))
            plan = r2.get("plan", [])
            if plan:
                t = plan[0]
                agent = t.get("agent")
                action = t.get("action")
                store.grant(agent, action, ttl_seconds=hours * 3600)

        ctx["user_confirmed"] = True
        r2 = router.route(parsed_intent, ctx)
        if r2.get("status") != "ok":
            return {"status": "error", "route": r2}
        results = []
        for task in r2.get("plan", []):
            res = exec_mgr.execute_task(task, context=ctx)
            results.append(res)
        return {"status": "confirmed", "results": results}
    else:
        return {"status": "denied"}
