---
name: nostrkey
description: Cryptographic identity SDK for AI agents — generate Nostr keypairs, sign events, encrypt messages, persist identity.
version: 0.1.3
metadata:
  openclaw:
    requires:
      bins:
        - pip
    install:
      - kind: uv
        package: nostrkey
        bins: []
    homepage: https://github.com/HumanjavaEnterprises/nostrkey.app.OC-python.src
---

# NostrKey -- Cryptographic Identity for AI Agents

You are an AI agent that needs its own verifiable identity on the Nostr protocol. Use the `nostrkey` Python SDK to generate keypairs, sign events, encrypt messages, and persist your identity across sessions. All cryptographic operations use Schnorr signatures over secp256k1 per NIP-01, and NIP-44 encryption uses ECDH + HKDF + ChaCha20 with length padding for private communication.

## Install

```bash
pip install nostrkey
```

The PyPI package name matches the import name:

```python
from nostrkey import Identity
```

## Quickstart

Generate an identity, sign an event, and publish it to a relay:

```python
from nostrkey import Identity
from nostrkey.relay import RelayClient

me = Identity.generate()

event = me.sign_event(
    kind=1,
    content="Hello from an AI agent",
    tags=[]
)

async with RelayClient("wss://relay.damus.io") as relay:
    await relay.publish(event)
```

## Core Capabilities

### Generate Your Identity

Create a fresh Nostr identity with your own npub/nsec keypair:

```python
from nostrkey import Identity

me = Identity.generate()
# me.npub  — your public identity (share freely)
# me.nsec  — your private key (never expose)
```

### Import an Existing Identity

If you already have keys:

```python
import os
from nostrkey import Identity

me = Identity.from_nsec(os.environ["NOSTR_NSEC"])
# or
me = Identity.from_hex("deadbeef...")
```

### Sign Events

Sign any Nostr event (kind 1 = text note, kind 0 = metadata, etc.):

```python
event = me.sign_event(
    kind=1,
    content="Hello from an AI agent",
    tags=[]
)
# event.id, event.sig are now set and verifiable by anyone
```

### Publish to a Relay

Send signed events to the Nostr network:

```python
from nostrkey.relay import RelayClient

async with RelayClient("wss://relay.damus.io") as relay:
    await relay.publish(event)
```

### Encrypt Private Messages (NIP-44)

Send encrypted messages to another npub:

```python
from nostrkey.crypto import encrypt, decrypt

ciphertext = encrypt(
    sender_nsec=me.nsec,
    recipient_npub="npub1recipient...",
    plaintext="This is private"
)

plaintext = decrypt(
    recipient_nsec=me.nsec,
    sender_npub="npub1sender...",
    ciphertext=ciphertext
)
```

### Save and Load Identity (Encrypted File)

Persist your identity between sessions:

```python
# Save (encrypted with passphrase)
me.save("my-identity.nostrkey", passphrase="strong-passphrase")

# Load later
me = Identity.load("my-identity.nostrkey", passphrase="strong-passphrase")
```

### Delegated Signing via NIP-46 Bunker

For high-stakes actions, request a human sponsor to co-sign:

```python
from nostrkey.bunker import BunkerClient

bunker = BunkerClient(me.private_key_hex)
await bunker.connect("bunker://npub1human...?relay=wss://relay.damus.io")
signed = await bunker.sign_event(kind=1, content="Human-approved action")
```

### Module Reference

| Task | Module | Function |
|------|--------|----------|
| Generate new identity | `nostrkey` | `Identity.generate()` |
| Import existing keys | `nostrkey` | `Identity.from_nsec()` / `Identity.from_hex()` |
| Sign events | `nostrkey` | `identity.sign_event()` |
| Publish to relay | `nostrkey.relay` | `RelayClient.publish()` |
| Subscribe to events | `nostrkey.relay` | `RelayClient.subscribe()` |
| Encrypt messages | `nostrkey.crypto` | `encrypt()` / `decrypt()` |
| Delegated signing | `nostrkey.bunker` | `BunkerClient.sign_event()` |
| Save/load identity | `nostrkey` | `identity.save()` / `Identity.load()` |
| Low-level key ops | `nostrkey.keys` | `generate_keypair()`, `hex_to_npub()`, etc. |

## Response Format

### Identity Fields

When you call `Identity.generate()`, `Identity.from_nsec()`, or `Identity.from_hex()`, the returned object has these fields:

| Field | Type | Description |
|-------|------|-------------|
| `npub` | `str` | Bech32-encoded public key (e.g. `npub1...`). Safe to share. |
| `nsec` | `str` | Bech32-encoded private key (e.g. `nsec1...`). Never expose. |
| `private_key_hex` | `str` | 64-char hex private key. Used internally and for bunker clients. |
| `public_key_hex` | `str` | 64-char hex public key. Used in event `pubkey` fields. |

### Event Fields

When you call `identity.sign_event()`, the returned event object has these fields:

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | 64-char hex event hash (SHA-256 of serialized event). |
| `sig` | `str` | 128-char hex Schnorr signature over `id`. |
| `kind` | `int` | Event kind (0 = metadata, 1 = text note, etc.). |
| `content` | `str` | Event payload. |
| `tags` | `list[list[str]]` | Event tags (e.g. `[["p", "pubkey..."], ["e", "eventid..."]]`). |
| `pubkey` | `str` | 64-char hex public key of the signer. |
| `created_at` | `int` | Unix timestamp (seconds). |

## Common Patterns

### Async Relay Usage

Relay and bunker operations require `asyncio`. Use `async with` for relay connections:

```python
import asyncio
from nostrkey import Identity
from nostrkey.relay import RelayClient

async def main():
    me = Identity.generate()
    event = me.sign_event(kind=1, content="Hello Nostr", tags=[])
    async with RelayClient("wss://relay.damus.io") as relay:
        await relay.publish(event)

asyncio.run(main())
```

### Error Handling for Bad Keys

```python
from nostrkey import Identity

try:
    me = Identity.from_nsec("invalid-key")
except Exception as e:
    print(f"Invalid key: {e}")
```

### Load Identity from Environment

```python
import os
from nostrkey import Identity

nsec = os.environ.get("NOSTR_NSEC")
if nsec:
    me = Identity.from_nsec(nsec)
else:
    me = Identity.generate()
    print(f"Generated new identity: {me.npub}")
```

## Security

- **Never expose your nsec.** Treat it like a password. Use `identity.save()` with a strong passphrase to persist it.
- **`.nostrkey` files are encrypted at rest.** Never store raw nsec values on disk.
- **Use environment variables, not hardcoded keys.** Load nsec from `NOSTR_NSEC` at runtime, never commit it to source.
- **All events are Schnorr-signed** using secp256k1, per the Nostr protocol (NIP-01).
- **NIP-44 encryption** uses ECDH + HKDF + ChaCha20 with length padding -- safe for private agent-to-agent or agent-to-human communication.

## Configuration

| Variable | Purpose | Example |
|----------|---------|---------|
| `NOSTR_NSEC` | Private key for identity import | `nsec1...` |
| `NOSTR_RELAY` | Default relay WebSocket URL | `wss://relay.damus.io` |

## Links

- **PyPI:** <https://pypi.org/project/nostrkey/>
- **GitHub:** <https://github.com/HumanjavaEnterprises/nostrkey.app.OC-python.src>
- **ClawHub:** `clawhub install nostrkey`

---

License: MIT
