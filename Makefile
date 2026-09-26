.PHONY: install run

install: .venv/bin/python
	.venv/bin/python -m pip install -r requirements.txt

.venv/bin/python:
	mise exec -- python -m venv .venv

run: .venv/bin/python
	.venv/bin/python -m src
