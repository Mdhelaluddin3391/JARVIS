import argparse
import datetime
from typing import Dict, Optional

from permissions.approvals import ApprovalStore


def list_approvals(path: Optional[str] = None) -> Dict[str, float]:
    store = ApprovalStore(path=path) if path else ApprovalStore()
    active = store.list_active()
    # print human friendly
    for k, exp in active.items():
        when = datetime.datetime.fromtimestamp(exp).isoformat()
        print(f"{k} -> expires at {when}")
    return active


def grant_approval(agent: str, action: Optional[str], hours: int = 1, path: Optional[str] = None) -> None:
    store = ApprovalStore(path=path) if path else ApprovalStore()
    ttl = int(hours) * 3600
    store.grant(agent, action, ttl_seconds=ttl)
    print(f"Granted approval for {agent}:{action} for {hours} hour(s)")


def revoke_approval(agent: str, action: Optional[str] = None, path: Optional[str] = None) -> bool:
    store = ApprovalStore(path=path) if path else ApprovalStore()
    existed = store.is_approved(agent, action)
    store.revoke(agent, action)
    if existed:
        print(f"Revoked approval for {agent}:{action}")
    else:
        print(f"No active approval found for {agent}:{action}")
    return existed


def main(argv=None):
    parser = argparse.ArgumentParser(prog="permissions-cli")
    sub = parser.add_subparsers(dest="cmd")

    sub_list = sub.add_parser("list", help="List active approvals")
    sub_list.add_argument("--path", help="approvals file path", default=None)

    sub_grant = sub.add_parser("grant", help="Grant approval")
    sub_grant.add_argument("agent", nargs="?", help="agent name")
    sub_grant.add_argument("action", nargs="?", help="action name or omit for wildcard", default=None)
    sub_grant.add_argument("--hours", type=int, help="grant duration in hours", default=1)
    sub_grant.add_argument("--path", help="approvals file path", default=None)

    sub_revoke = sub.add_parser("revoke", help="Revoke approval")
    sub_revoke.add_argument("agent", help="agent name")
    sub_revoke.add_argument("action", nargs="?", help="action name or omit for wildcard", default=None)
    sub_revoke.add_argument("--path", help="approvals file path", default=None)

    args = parser.parse_args(argv)
    if args.cmd == "list":
        list_approvals(path=args.path)
    elif args.cmd == "grant":
        agent = args.agent
        action = args.action
        hours = args.hours
        # Interactive prompts if missing
        if not agent:
            agent = input("Agent name: ").strip()
        if action is None:
            action = input("Action (leave empty for wildcard): ").strip() or None
        grant_approval(agent, action, hours=hours, path=args.path)
    elif args.cmd == "revoke":
        revoke_approval(args.agent, args.action, path=args.path)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
