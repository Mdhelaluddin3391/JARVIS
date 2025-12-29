PYTHON ?= python3
VENV = .venv
ACT = . $(VENV)/bin/activate && 

.PHONY: init install lint test demo

init:
	$(PYTHON) -m venv $(VENV)
	$(ACT) pip install -U pip setuptools

install:
	$(ACT) pip install -r requirements.txt

lint:
	$(ACT) pip install pre-commit && pre-commit run --all-files
	$(ACT) pip install black isort flake8
	$(ACT) black . && $(ACT) isort . && $(ACT) flake8

test:
	$(ACT) pip install -r requirements.txt
	$(ACT) pip install -r requirements-dev.txt
	$(ACT) pytest -q

coverage:
	$(ACT) pip install -r requirements-dev.txt
	$(ACT) python -m pytest --maxfail=1 --disable-warnings --cov=.


approvals-list:
	$(ACT) $(PYTHON) -m permissions.cli list

approvals-grant:
	@# Usage: make approvals-grant agent=<agent> action=<action> hours=<hours>
	$(ACT) $(PYTHON) -m permissions.cli grant $(agent) $(action) --hours=$(hours)

approvals-revoke:
	@# Usage: make approvals-revoke agent=<agent> action=<action>
	$(ACT) $(PYTHON) -m permissions.cli revoke $(agent) $(action)


demo:
	$(ACT) $(PYTHON) main.py
