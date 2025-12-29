import json
from shadow_learning.observer.export_dataset import export_dataset


def test_export_filters_pii(tmp_path):
    events = tmp_path / "events.jsonl"
    out = tmp_path / "out.jsonl"
    sample = {"id": "1", "event": {"type": "test", "user_id": "abc123", "email": "me@example.com", "text": "hello"}}
    events.write_text(json.dumps(sample) + "\n")

    n = export_dataset(str(events), str(out))
    assert n == 1
    lines = out.read_text().splitlines()
    data = json.loads(lines[0])
    assert data["event"]["user_id"] == "[REDACTED]"
    assert "[REDACTED]" in data["event"]["email"] or data["event"]["email"] == "[REDACTED]"
