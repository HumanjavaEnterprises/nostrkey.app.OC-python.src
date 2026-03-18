# TOOLS.md Snippet — NostrKey

Paste the block below into your agent's `TOOLS.md` file (in the workspace root).
This tells the agent that the nostrkey skill is available and gives it the explicit file path.

> **Why the full path?** Smaller models (e.g., Qwen3 8B) may not reliably construct
> the correct file path from just a filename. Including the absolute path lets the
> agent's file-read tool find it on the first try.

---

## Paste this into your TOOLS.md:

Replace `/home/openclaw/.openclaw/workspace` with your actual OC workspace path if different.

```markdown
## Available Skills

These skill files are in your workspace. Read them when you need to use the capability.

- **NostrKey SDK** — file path: `/home/openclaw/.openclaw/workspace/nostrkey-SKILL.md`
  Nostr identity SDK (Python). Generate keypairs, sign events, encrypt messages, import existing keys, save/load encrypted identity files. The `nostrkey` package is pre-installed via pip — you can `from nostrkey import Identity` directly in Python code. Read the file at the path above for full usage instructions.
```

---

## If your agent doesn't have a TOOLS.md

Create one in the workspace root with this content:

```markdown
# TOOLS.md - Available Tools & Skills

## Available Skills

These skill files are in your workspace. Read them when you need to use the capability.

- **NostrKey SDK** — file path: `/home/openclaw/.openclaw/workspace/nostrkey-SKILL.md`
  Nostr identity SDK (Python). Generate keypairs, sign events, encrypt messages, import existing keys, save/load encrypted identity files. The `nostrkey` package is pre-installed via pip — you can `from nostrkey import Identity` directly in Python code. Read the file at the path above for full usage instructions.

## Environment Notes

Add any environment-specific notes here (device names, SSH hosts, API endpoints, etc.).
```
