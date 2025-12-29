from llm_runtime.manager import LocalAdapter, RemoteAdapter, LLMSelector


def test_selector_prefers_local_by_default():
    local = LocalAdapter()
    remote = RemoteAdapter()
    sel = LLMSelector(local, remote)
    adapter = sel.select(text="short request", complexity_hint=0)
    assert isinstance(adapter, LocalAdapter)


def test_selector_chooses_remote_for_long_text():
    local = LocalAdapter()
    remote = RemoteAdapter()
    sel = LLMSelector(local, remote)
    adapter = sel.select(text="x" * 500, complexity_hint=0)
    assert isinstance(adapter, RemoteAdapter)


def test_selector_forced_preference():
    local = LocalAdapter()
    remote = RemoteAdapter()
    sel = LLMSelector(local, remote)
    assert isinstance(sel.select(text="any", prefer="remote"), RemoteAdapter)
    assert isinstance(sel.select(text="any", prefer="local"), LocalAdapter)
