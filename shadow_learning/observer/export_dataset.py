import json
import os
import re
from typing import Generator

PII_KEYS = {"user_id", "email", "phone", "ssn"}
EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")


def _filter_pii(event: dict) -> dict:
    e = json.loads(json.dumps(event))  # deep copy
    payload = e.get("event", {})
    if isinstance(payload, dict):
        # remove known keys in payload
        for k in list(payload.keys()):
            if k in PII_KEYS:
                payload[k] = "[REDACTED]"
        # redact emails in string fields
        for k, v in list(payload.items()):
            if isinstance(v, str) and EMAIL_RE.search(v):
                payload[k] = EMAIL_RE.sub("[REDACTED]", v)
    e["event"] = payload
    return e


def export_dataset(events_path: str, out_path: str) -> int:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    count = 0
    if not os.path.exists(events_path):
        return 0
    with open(events_path, "r", encoding="utf-8") as fh_in, open(out_path, "w", encoding="utf-8") as fh_out:
        for line in fh_in:
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            e_f = _filter_pii(e)
            fh_out.write(json.dumps(e_f) + "\n")
            count += 1
    return count


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("usage: export_dataset.py <events.jsonl> <out.jsonl>")
        raise SystemExit(2)
    n = export_dataset(sys.argv[1], sys.argv[2])
    print(f"Exported {n} events")