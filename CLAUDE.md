# CLAUDE.md — nostrkey.app.OC-python.src

## What This Is
Open-source Python SDK for OpenClaw AI entities to generate and manage their own Nostr cryptographic identities. The Python equivalent of the NostrKey browser extension — but for bots.

## Ecosystem Position
NostrKey (browser extension) is for humans. This SDK is for AI entities (OpenClaw bots) that need their own npub/nsec keypairs, event signing, encryption, and optionally NIP-46 bunker delegation to a human sponsor.

## Package Name
`nostrkey` on PyPI — `pip install nostrkey`

## Module Structure
- `nostrkey.keys` — keypair generation, bech32 encoding (npub/nsec), hex conversion
- `nostrkey.events` — create, serialize, hash, and sign Nostr events
- `nostrkey.crypto` — NIP-44 encryption/decryption for private data
- `nostrkey.bunker` — NIP-46 bunker client for delegated signing to a human's NostrKey
- `nostrkey.relay` — WebSocket relay client (publish events, subscribe to filters)
- `nostrkey.identity` — high-level OpenClaw identity management (generate, store, load)

## Key Design Decisions
- Pure Python where possible, minimal dependencies
- secp256k1 for cryptographic operations (via `secp256k1` or `coincurve` package)
- WebSocket via `websockets` package
- Async-first API (asyncio)
- Type hints throughout
- MIT licensed, open source

## Conventions
- kebab-case for file names in docs/config, snake_case for Python modules
- Tests in `tests/` using pytest
- Examples in `examples/`
- No cryptocurrency/token functionality — identity only

## Related Repos
- `nostrkey.browser.plugin.src` — NostrKey browser extension (JS, the human equivalent)
- `nostr-crypto-utils` — TypeScript crypto library (reference implementation for crypto operations)
- `loginwithnostr.web.landingpage.src` — Landing page, `/openclaw` route will reference this SDK
- `nostrkey.bizdocs.src` — Business docs (OpenClaw GTM, payment model)
