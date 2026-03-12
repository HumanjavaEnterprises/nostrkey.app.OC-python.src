# TODO — NostrKey Python SDK

## ClawHub / OpenClaw Integration

- [ ] Publish skill to ClawHub registry (`clawhub publish ./clawhub --slug nostrkey`)
- [ ] Add CI step to auto-publish skill on PyPI release (keep versions in sync)
- [ ] Set up own OpenClaw instance with Nostr channel to dogfood the skill
- [ ] Test skill discovery via ClawHub vector search (does "nostr identity for my bot" find it?)
- [ ] Submit to [awesome-openclaw-skills](https://github.com/VoltAgent/awesome-openclaw-skills) list

## SDK Features

- [ ] Replace pure-Python ChaCha20 (`_chacha20.py`) with C-backed implementation for production use
- [ ] Add NIP-05 identity verification (DNS-based `user@domain` → npub mapping)
- [ ] Add NIP-65 relay list metadata support
- [ ] Add CLI entrypoint (`nostrkey generate`, `nostrkey sign`, `nostrkey encrypt`) for direct terminal use
- [ ] Add relay pool support (publish to multiple relays simultaneously)
- [ ] Add event kind helpers (kind 0 metadata, kind 3 contact list, kind 10002 relay list)

## Testing & Quality

- [ ] Add integration tests against a local relay (e.g. `strfry` in Docker)
- [ ] Add NIP-44 test vectors from the official spec
- [ ] Add bunker integration tests with mock signer
- [ ] Set up GitHub Actions CI (lint + test on Python 3.10–3.13)
- [ ] Add code coverage reporting

## Documentation & Distribution

- [ ] Add CHANGELOG.md (start tracking from v0.1.1)
- [ ] Publish to PyPI (currently local builds only in `dist/`)
- [ ] Add badges to README (PyPI version, Python versions, license, ClawHub)
- [ ] Add contributing guide (CONTRIBUTING.md)
- [ ] Add docs to loginwithnostr.com/openclaw route

## Security

- [ ] Security audit of NIP-44 encryption implementation
- [ ] Add key rotation support (generate new keypair, migrate identity)
- [ ] Add passphrase strength validation on `identity.save()`
- [ ] Consider hardware key support (YubiKey / FIDO2 for nsec storage)

## Ecosystem

- [ ] Cross-test with NostrKey browser extension (human ↔ bot encrypted messaging)
- [ ] Build example: OpenClaw bot that manages its own Nostr profile
- [ ] Build example: two bots communicating via NIP-44 encrypted DMs
- [ ] Explore nostrkeep integration (vault-style key management for fleets of bots)
