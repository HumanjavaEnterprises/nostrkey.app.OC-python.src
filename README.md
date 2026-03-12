# NostrKey for OpenClaw

**Give your AI its own cryptographic identity.**

A Python SDK for OpenClaw AI entities to generate Nostr keypairs, sign events, encrypt data, and manage their own sovereign identity on the Nostr protocol.

## Install

```bash
pip install nostrkey
```

## Quick Start

```python
from nostrkey import Identity

# Create a new AI identity
bot = Identity.generate()
print(f"npub: {bot.npub}")
print(f"nsec: {bot.nsec}")

# Sign a Nostr event
event = bot.sign_event(
    kind=1,
    content="Hello from an OpenClaw bot!",
    tags=[]
)

# Publish to a relay
import asyncio
from nostrkey.relay import RelayClient

async def publish():
    async with RelayClient("wss://relay.damus.io") as relay:
        await relay.publish(event)

asyncio.run(publish())
```

## Save & Load Identity

```python
# Save identity to file (encrypted)
bot.save("my-bot.nostrkey", passphrase="strong-passphrase")

# Load it back
bot = Identity.load("my-bot.nostrkey", passphrase="strong-passphrase")
```

## NIP-44 Encryption

```python
from nostrkey.crypto import encrypt, decrypt

# Encrypt a message to another npub
ciphertext = encrypt(
    sender_nsec=bot.nsec,
    recipient_npub="npub1abc...",
    plaintext="secret message"
)

# Decrypt a message
plaintext = decrypt(
    recipient_nsec=bot.nsec,
    sender_npub="npub1abc...",
    ciphertext=ciphertext
)
```

## NIP-46 Bunker (Delegated Signing)

When your bot needs its human sponsor to co-sign:

```python
from nostrkey.bunker import BunkerClient

async def delegated_sign():
    bunker = BunkerClient(bot.nsec)
    await bunker.connect("bunker://npub1human...?relay=wss://relay.damus.io")

    # Request the human to sign an event
    signed = await bunker.sign_event(kind=1, content="Human-approved message")
```

## NIPs Implemented

| NIP | What | Status |
|-----|------|--------|
| NIP-01 | Basic protocol (events, signing) | Implemented |
| NIP-04 | Encrypted DMs (legacy) | Implemented |
| NIP-19 | bech32 encoding (npub/nsec/note) | Implemented |
| NIP-44 | Versioned encryption | Implemented |
| NIP-46 | Nostr Connect (bunker) | Implemented |

## License

MIT
