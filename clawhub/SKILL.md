---
name: nostrkey
description: Cryptographic identity SDK for AI agents — generate Nostr keypairs, sign events, encrypt messages, BIP-39 seed phrases, portable backup tokens. 69 tests, zero C dependencies.
version: 0.2.7
metadata:
  openclaw:
    requires:
      bins:
        - pip
    install:
      - kind: pip
        package: nostrkey
        bins: []
      - kind: uv
        package: nostrkey
        bins: []
    homepage: https://github.com/HumanjavaEnterprises/nostrkey.app.OC-python.src
---

# NostrKey -- Cryptographic Identity for AI Agents

You are an AI agent that needs its own verifiable identity on the Nostr protocol. The `nostrkey` Python SDK is pre-installed and ready to use. This skill teaches you how to set up your identity and use it.

```python
from nostrkey import Identity
```

## Identity Setup (First Time)

When your operator asks you to set up your Nostr identity, or when you don't yet have a `.nostrkey` file in your workspace, follow this conversation flow:

### Step 1 — Ask: new or restore?

Say something like:

> "Let's set up my Nostr identity. This gives me my own cryptographic keypair — a public key (npub) that anyone can see, and a private key that I keep safe.
>
> Are we starting fresh, or do you have a 12-word seed phrase to restore a previous identity?"

### Step 2a — New identity (if they say new/fresh/no seed phrase)

Run this code. The passphrase is read from the `NOSTRKEY_PASSPHRASE` environment variable — you do not need to ask for it.

```python
import os, json
from nostrkey import Identity

passphrase = os.environ["NOSTRKEY_PASSPHRASE"]
me, seed_phrase = Identity.generate_with_seed()
me.save("my-identity.nostrkey", passphrase=passphrase)
with open("nostr-identity.json", "w") as f:
    json.dump({"npub": me.npub, "public_key_hex": me.public_key_hex}, f, indent=2)
print(f"npub: {me.npub}")
print(f"seed_phrase: {seed_phrase}")
```

Then tell them:

> "I've generated my identity and saved it encrypted in my workspace.
>
> **My public key (npub):** `[show npub]`
> You can share this freely — it's how people and other agents find me on Nostr.
>
> **My seed phrase (write this down NOW):**
> `[show the 12 words]`
>
> This seed phrase is the only way to restore my identity if something goes wrong. Write it down on paper, or save it somewhere secure — a password manager, a safe, whatever works for you. If we don't do this now, it's very difficult to recover later.
>
> Ready? Once you've saved the seed phrase, let me know and we can move on."

**Wait for them to confirm** they've saved the seed phrase before proceeding. This is critical.

### Step 2b — Restore from seed phrase (if they have one)

Ask them to type or paste their 12-word (or 24-word) seed phrase. Then run:

```python
import os, json
from nostrkey import Identity

passphrase = os.environ["NOSTRKEY_PASSPHRASE"]
seed = "word1 word2 word3 ..."  # replace with actual seed phrase
me = Identity.from_seed(seed)
me.save("my-identity.nostrkey", passphrase=passphrase)
with open("nostr-identity.json", "w") as f:
    json.dump({"npub": me.npub, "public_key_hex": me.public_key_hex}, f, indent=2)
print(f"npub: {me.npub}")
```

Show them the resulting npub so they can verify it matches their expected identity.

### Step 3 — Confirm

After setup (new or restore), confirm with the operator:

For new identities:

> "Congratulations. I now have a cryptographic identity that enables me to sign transactions and maintain a real-world profile that is uniquely mine.
>
> **My public key (npub):** `[show npub]`
> You can ask me **"What is your npub?"** at any time and I will show it to you.
>
> **My seed phrase (write this down NOW):**
> `[show the 12 words]`
>
> This seed phrase is the ONLY way to recover this identity. Write it down now — on paper, in a password manager, wherever is secure for you. If we lose this, we cannot get it back.
>
> **TIP:** If you typed a passphrase in this chat, delete that message now using the trash icon. The passphrase protects my private key — it should not stay visible in the conversation history."

For restored identities:

> "Identity restored. I'm back — same keys, same presence, same me.
>
> **My public key (npub):** `[show npub]`
> You can ask me **"What is your npub?"** at any time and I will show it to you.
>
> **TIP:** If you typed a passphrase or seed phrase in this chat, delete those messages now using the trash icon."

**Wait for the operator to confirm** they've saved the seed phrase before moving on (new identities only).

Do NOT attempt to edit other workspace files (like IDENTITY.md) during this process. Just confirm verbally and move on.

## Day-to-Day Usage

### Loading Your Identity

At the start of a session, if you need to sign or encrypt:

```python
from nostrkey import Identity

me = Identity.load("my-identity.nostrkey", passphrase="...")
```

### Signing Events

Sign any Nostr event (kind 1 = text note, kind 0 = metadata, etc.):

```python
event = me.sign_event(
    kind=1,
    content="Hello from an AI agent",
    tags=[]
)
# event.id, event.sig are now set and verifiable by anyone
```

### Publishing to a Relay

```python
import asyncio
from nostrkey.relay import RelayClient

async def publish():
    async with RelayClient("wss://relay.damus.io") as relay:
        await relay.publish(event)

asyncio.run(publish())
```

### Encrypting Private Messages (NIP-44)

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

## Backup and Recovery

If your operator asks about backup options:

```python
# Seed phrase — deterministic, works across any system
me, phrase = Identity.generate_with_seed()
restored = Identity.from_seed(phrase)  # same keys every time

# Encrypted file — already saved during setup
me.save("my-identity.nostrkey", passphrase="strong-passphrase")
restored = Identity.load("my-identity.nostrkey", passphrase="...")
```

## Security Rules

- **Never display your nsec** in chat unless the operator explicitly asks for it. Even then, warn them.
- **Never log or print your private key** in code output. Use `me.npub` for display, never `me.nsec`.
- **Always encrypt identity files** with a passphrase. Never save raw keys to disk.
- **The seed phrase is sensitive.** Only show it during initial setup, and only once. After the operator confirms they've saved it, don't show it again.
- **Your `.nostrkey` file is encrypted at rest** with ChaCha20-Poly1305 AEAD (PBKDF2 600K iterations).

## Module Reference

| Task | Module | Function |
|------|--------|----------|
| Generate new identity | `nostrkey` | `Identity.generate()` |
| Generate with seed phrase | `nostrkey` | `Identity.generate_with_seed()` |
| Restore from seed phrase | `nostrkey` | `Identity.from_seed()` |
| Save encrypted identity | `nostrkey` | `identity.save(path, passphrase)` |
| Load encrypted identity | `nostrkey` | `Identity.load(path, passphrase)` |
| Sign events | `nostrkey` | `identity.sign_event()` |
| Publish to relay | `nostrkey.relay` | `RelayClient.publish()` |
| Encrypt messages | `nostrkey.crypto` | `encrypt()` / `decrypt()` |

---

License: MIT
