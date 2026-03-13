# NostrKey for OpenClaw

**Give your AI its own cryptographic identity.**

A Python SDK for OpenClaw AI entities to generate Nostr keypairs, sign events, encrypt data, and manage their own identity on the Nostr protocol.

## Why?

AI agents need identity. Not a shared API key — their *own* keypair, their own signature, their own verifiable presence on an open protocol. That's what this SDK gives them.

**A few things your bot can do with its own npub:**

- **Sign its own work** — every post, response, or action is cryptographically signed. Anyone can verify it came from your bot, not an impersonator.
- **Send and receive encrypted messages** — private communication between your bot and its human, or between bots, using NIP-44 encryption. No platform middleman.
- **Persist memory across sessions** — save encrypted identity files and reload them. Your bot picks up where it left off.
- **Publish to the Nostr network** — your bot can post notes, respond to mentions, and interact on any Nostr relay. It's a first-class participant, not a wrapper around someone else's account.
- **Delegate sensitive actions to a human** — via NIP-46 bunker, your bot can request its human sponsor to co-sign high-stakes events. The human stays in the loop without holding the bot's keys.

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
    bunker = BunkerClient(bot.private_key_hex)
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

## OpenClaw Skill (ClawHub)

This repo includes an OpenClaw skill in `clawhub/` so AI agents can discover and use NostrKey directly from the [ClawHub registry](https://clawhub.ai/).

**Install the skill in your OpenClaw instance:**

```bash
clawhub install nostrkey
```

**Or publish from source:**

```bash
clawhub publish ./clawhub --slug nostrkey --version 0.1.2
```

The skill teaches OpenClaw agents how to generate identities, sign events, encrypt messages, and persist keys — all using the `nostrkey` pip package under the hood. See `clawhub/SKILL.md` for the full skill definition.

## License

MIT
