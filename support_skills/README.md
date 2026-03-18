# Support Skills — OpenClaw Workspace Files

These are ready-to-deploy files for OpenClaw operators whose agents don't support `clawhub install` or lack file-discovery tools.

## The Problem

Most OpenClaw deployments today have three gaps that block skill adoption:

1. **No `clawhub install`** — the agent doesn't recognize it as a command, especially on smaller local models (e.g., Qwen3 8B).
2. **No file discovery** — OC agents can't list directory contents. Files added to the workspace after bootstrap are invisible unless explicitly referenced.
3. **No runtime `pip install`** — OC containers typically run with read-only root filesystems. Python packages must be baked into the Docker image at build time.

## What's Here

| File | Purpose | Where to Put It |
|------|---------|-----------------|
| `nostrkey-SKILL.md` | Agent-facing skill definition. Teaches the agent how to use the `nostrkey` SDK — generate keys, sign events, encrypt, import/export. | Copy into OC workspace root |
| `TOOLS-snippet.md` | A block to paste into your agent's `TOOLS.md` so it knows the skill file exists and where to find it. | Paste into your existing `TOOLS.md` |

## Setup

### Step 1 — Install the SDK in your Docker image

Add this to your Dockerfile (before switching to the non-root user):

```dockerfile
RUN pip3 install --no-cache-dir --break-system-packages nostrkey==0.2.3
```

Then rebuild:

```bash
docker compose build --no-cache <your-oc-service> && docker compose up -d <your-oc-service>
```

### Step 2 — Copy the skill file into the workspace

The workspace path varies by deployment. Find yours:

```bash
docker exec <container> find /home -name "BOOTSTRAP.md" -type f 2>/dev/null
```

The directory containing `BOOTSTRAP.md` is your OC workspace root. Copy the skill file there:

```bash
docker cp support_skills/nostrkey-SKILL.md <container>:/path/to/workspace/nostrkey-SKILL.md
```

Or mount it as a volume in your `docker-compose.yml`:

```yaml
volumes:
  - ./support_skills/nostrkey-SKILL.md:/home/openclaw/.openclaw/workspace/nostrkey-SKILL.md:ro
```

### Step 3 — Tell the agent the file exists

OC agents can't discover new files on their own. Paste the contents of `TOOLS-snippet.md` into your agent's `TOOLS.md` (in the workspace root). This tells the agent what skills are available and where to find them.

If your agent doesn't have a `TOOLS.md` yet, you can create one — or add the reference to `BOOTSTRAP.md` instead.

### Step 4 — Verify

Restart or re-read context, then ask your agent:

> Read your TOOLS.md, then read nostrkey-SKILL.md. What can you do with nostrkey?

If the agent reads the file and explains the SDK, you're good.

## Reusable Pattern

This approach isn't specific to nostrkey. Any OC skill can ship a `support_skills/` folder with the same structure:

```
support_skills/
├── README.md           ← deployment guide (this file)
├── <skill>-SKILL.md    ← agent-facing skill definition
└── TOOLS-snippet.md    ← paste into TOOLS.md so the agent can find it
```

Until `clawhub install` works reliably across all OC deployments and models, this is the most reliable way to get skills into an agent's hands.
