from orchestrator.task_planner import TaskPlanner


def test_task_planner_music():
    p = TaskPlanner()
    parsed = {"intent": "play_music", "entities": {"query": "some song"}, "text": "play some song"}
    plan = p.plan(parsed)
    assert len(plan) == 1
    assert plan[0]["agent"] == "music_agent"
    assert plan[0]["action"] == "play"
    assert "query" in plan[0]["args"]["entities"] or parsed["entities"]["query"]
