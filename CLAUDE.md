# CLAUDE.md — nostrkey

## What this is
Nostr identity SDK for OpenClaw AI agents — generate keys, sign events, encrypt data, run a NIP-46 bunker. Part of the open-source OpenClaw Nostr toolkit. MIT licensed.

## Install
```
pip install nostrkey
```

## Develop
```
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
python -m pytest -q     # tests
python -m build         # sdist + wheel
```

## Layout
- `src/nostrkey/` — package source
- `tests/` — pytest suite
- `clawhub/` — ClawHub skill metadata (SKILL.md, metadata.json)

## Conventions
- Python + pyproject (hatchling). Pure-Python crypto (`cryptography`), zero native build deps.
- Public, MIT-licensed, open source.
