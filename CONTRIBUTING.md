# Contributing to JARVIS

Thanks for your interest in contributing! This document gives a quick developer setup and contribution guidelines.

## Quickstart (dev)

1. Create virtual environment

   python3 -m venv .venv
   . .venv/bin/activate

2. Install dependencies

   pip install -U pip
   pip install -r requirements.txt

3. Run tests

   pytest

## Code style
- Formatting: black
- Imports: isort
- Type hints encouraged

## Workflow
- Fork the repo and create a feature branch `feature/<short-description>`
- Open a PR against `main` with a clear description and tests
- Add unit tests for new features and bug fixes

## Issues
- Use labels to categorize: `bug`, `enhancement`, `proposal`

## Communication
- Use PR descriptions and link related issues
- Add small design notes for larger features in `docs/`
