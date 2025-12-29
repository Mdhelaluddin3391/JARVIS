import json

from core.orchestrator.event_bus import EventBus


def test_append_and_read_events(tmp_path):
    path = tmp_path / "events.jsonl"
    eb = EventBus(path=str(path))

    e = {"type": "test.event", "payload": {"x": 1}}
    envelope = eb.append_event(e, version="v1")

    events = list(eb.read_events())
    assert len(events) == 1
    assert events[0]["id"] == envelope["id"]
    assert events[0]["event"]["type"] == "test.event"


def test_validation_and_tail(tmp_path):
    path = tmp_path / "events.jsonl"
    eb = EventBus(path=str(path))

    # Invalid event must raise
    try:
        eb.append_event({"payload": 1})
        assert False, "Validation should have raised"
    except ValueError:
        pass

    # Add multiple events and verify tail
    for i in range(5):
        eb.append_event({"type": f"e{i}", "i": i})

    last2 = eb.tail(2)
    assert len(last2) == 2
    assert last2[-1]["event"]["type"] == "e4"
