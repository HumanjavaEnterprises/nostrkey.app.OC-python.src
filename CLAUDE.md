# CLAUDE.md — nostrkey.app.OC-python.src

## What This Is
Open-source Python SDK for OpenClaw AI entities to generate and manage their own Nostr cryptographic identities. The Python equivalent of the NostrKey browser extension — but for bots.

## Ecosystem Position
NostrKey (browser extension) is for humans. This SDK is for AI entities (OpenClaw bots) that need their own npub/nsec keypairs, event signing, encryption, and optionally NIP-46 bunker delegation to a human sponsor.

## Package Name
`nostrkey` on PyPI — `pip install nostrkey`

## Current Version
v0.2.0 — Published on PyPI and ClawHub (2026-03-17). Red-team audited, 49 tests, zero C dependencies.

## Module Structure
- `nostrkey.identity` — high-level OpenClaw identity management (generate, store, load)
- `nostrkey.keys` — keypair generation, bech32 encoding (npub/nsec), hex conversion, private key validation
- `nostrkey.events` — create, serialize, hash, and sign Nostr events (BIP-340 Schnorr)
- `nostrkey.crypto` — NIP-44 encryption/decryption (ECDH + HKDF + ChaCha20, spec-compliant padding)
- `nostrkey.bunker` — NIP-46 bunker client for delegated signing to a human's NostrKey
- `nostrkey.relay` — WebSocket relay client (publish events, subscribe to filters, SSRF protection)
- `nostrkey._secp256k1` — BIP-340 Schnorr + ECDH via `cryptography` package (internal)
- `nostrkey._chacha20` — Pure-Python ChaCha20 for NIP-44 (internal)

## Key Design Decisions
- Zero C dependencies — uses `cryptography` package (ships binary wheels for all platforms)
- Replaced `secp256k1` C binding with `_secp256k1.py` using `cryptography`'s EC primitives + pure-Python BIP-340 Schnorr (2026-03-17)
- Identity files use ChaCha20-Poly1305 AEAD (v3 format), backward-compatible with v2 (XOR + HMAC)
- v1 identity files no longer supported (unauthenticated)
- Async-first API (asyncio) for relay and bunker operations
- Type hints throughout
- MIT licensed, open source

## Dependencies
- `cryptography>=42.0,<45.0` — ECDH, ChaCha20-Poly1305, key generation (OpenSSL-backed, binary wheels)
- `websockets>=12.0,<15.0` — relay and bunker WebSocket connections
- `bech32>=1.2.0,<2.0` — npub/nsec encoding

## Security (v0.2.0 red team, 2026-03-17)
15 findings fixed from Tavin's red team + independent audit:
- ChaCha20-Poly1305 AEAD for identity files (PBKDF2 600K iterations)
- NIP-44 spec-compliant ECDH (raw x-coordinate) and padding
- Private key range validation (reject zero, >= N)
- Relay SSRF protection (blocks localhost, private IPs, reserved addresses)
- Path traversal protection on identity save/load
- Bunker response pubkey verification
- secrets.token_bytes() for all randomness
- Log scrubbing (no key material in logs)
- Best-effort key zeroing (Identity.wipe())
- Dataclass fields repr=False

## Conventions
- kebab-case for file names in docs/config, snake_case for Python modules
- Tests in `tests/` using pytest (49 tests across 5 files)
- Examples in `examples/`
- ClawHub skill definition in `clawhub/` (SKILL.md + metadata.json)
- No cryptocurrency/token functionality — identity only
- After code changes: run `python3 -m pytest tests/ -v` before committing

## ClawHub Skill
The `clawhub/` directory contains the OpenClaw skill bundle for publishing to ClawHub. Keep `metadata.json` version in sync with `pyproject.toml` version on each release. The `SKILL.md` is the agent-facing instruction set — it should reflect the current public API.

**Published:** `nostrkey@0.2.0` on ClawHub (2026-03-17). Install via `clawhub install nostrkey`.
**Publish command:** `npx clawhub publish ./clawhub --slug nostrkey --name "NostrKey" --version X.Y.Z --tags latest --changelog "..."`
**Important:** The CLI is `npx clawhub` (npm package), NOT the Python `clawhub` package. Must `npx clawhub login` first (GitHub auth). ClawHub rejects re-publishing existing versions — always bump.
**Examples:** `clawhub/examples/` — generate_and_post.py, encrypt_dm.py, delegated_signing.py

## Related Repos
- `nostrkey.browser.plugin.src` — NostrKey browser extension (JS, the human equivalent)
- `nostr-crypto-utils` — TypeScript crypto library (reference implementation for crypto operations)
- `loginwithnostr.web.landingpage.src` — Landing page, `/openclaw` route references this SDK
- `nostrkey.bizdocs.src` — Business docs (OpenClaw GTM, payment model)
- Docs page: `nostrkey.com/python` (in `nostrkey.browser.plugin.src/docs/python.html`)
