# NostrKey for OpenClaw

**Give your AI its own cryptographic identity.**

A Python SDK for OpenClaw AI entities to generate Nostr keypairs, sign events, encrypt data, and manage their own identity on the Nostr protocol.

**v0.2.5** — OC-ready identity onboarding, support_skills for manual deployment, BIP-39 seed phrases, portable backup tokens, 69 tests. Zero C dependencies. `pip install nostrkey` just works.

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

No C compiler, no system libraries, no Homebrew. The `cryptography` package (the only native dependency) ships pre-built wheels for macOS, Linux, and Windows.

**Python 3.10 – 3.14 supported.**

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

## Backup & Restore

Three ways to back up an identity — choose what fits your context:

```python
# 1. Seed phrase — 12 words, write on paper, deterministic
bot, phrase = Identity.generate_with_seed()
print(phrase)  # "adult carpet exit glance grant office ..."
restored = Identity.from_seed(phrase)  # same keys every time

# 2. Encrypted token — paste into a password manager or env var
token = bot.export_token(passphrase="strong-passphrase")
print(token)  # "nostrkey:v3:base64data..."
restored = Identity.from_token(token, passphrase="strong-passphrase")

# 3. Encrypted file — persistent storage
bot.save("my-bot.nostrkey", passphrase="strong-passphrase")
restored = Identity.load("my-bot.nostrkey", passphrase="strong-passphrase")

# Backup card — structured view of all key formats
card = bot.backup_card()
print(card["npub"])     # public key
print(card["nsec"])     # private key — store securely!
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

## Modules

| Module | What |
|--------|------|
| `nostrkey.identity` | High-level identity management — generate, import, sign, save, load, seed phrases, tokens |
| `nostrkey.seed` | BIP-39 seed phrase generation, validation, and NIP-06 key derivation |
| `nostrkey.keys` | Keypair generation, bech32 encoding (npub/nsec), hex conversion |
| `nostrkey.events` | Create, serialize, hash, and sign Nostr events (NIP-01) |
| `nostrkey.crypto` | NIP-44 versioned encryption and decryption |
| `nostrkey.bunker` | NIP-46 bunker client for delegated signing |
| `nostrkey.relay` | Async WebSocket relay client — publish events, subscribe to filters |

## NIPs Implemented

| NIP | What | Status |
|-----|------|--------|
| NIP-01 | Basic protocol (events, signing) | Implemented |
| NIP-04 | Encrypted DMs (legacy) | Implemented |
| NIP-06 | Key derivation from seed phrase | Implemented |
| NIP-19 | bech32 encoding (npub/nsec/note) | Implemented |
| NIP-44 | Versioned encryption | Implemented |
| NIP-46 | Nostr Connect (bunker) | Implemented |

## Security

v0.2.0 was red-team audited with 15 findings fixed:

- **Identity files** encrypted with ChaCha20-Poly1305 AEAD (PBKDF2 600K iterations)
- **Private key validation** rejects zero keys and out-of-range values
- **Relay SSRF protection** blocks localhost, private IPs, reserved addresses
- **Path traversal protection** on identity save/load
- **Bunker response verification** confirms signer pubkey matches expected remote
- **NIP-44 spec compliance** — correct padding algorithm and ECDH output
- **Constant-time comparisons** via `hmac.compare_digest` for all secret checks
- **No key material in logs** — bunker logs scrubbed to DEBUG with type-only info
- **BIP-39 seed phrases** with correct y-parity BIP-32 derivation and zero-key guards
- **Portable encrypted tokens** using the same ChaCha20-Poly1305 AEAD as file save
- **69 tests** covering keys, events, identity, crypto, seed phrases, tokens, relay validation, and edge cases

**Dependencies:** `cryptography` (OpenSSL-backed, ships binary wheels), `websockets`, `bech32`, `mnemonic`. No C compiler required.

## OpenClaw Deployment

### Quick Start (ClawHub)

If your OC version supports it:

```bash
clawhub install nostrkey
```

### Manual Setup

Most OC deployments today can't use `clawhub install` — agents may not recognize the command, can't install pip packages at runtime (read-only filesystem), and can't discover files added to the workspace after bootstrap.

The `support_skills/` folder contains ready-to-deploy workspace files that solve all three problems. See [`support_skills/README.md`](support_skills/README.md) for the full walkthrough.

**Short version:**

1. Add `nostrkey` to your Dockerfile:
   ```dockerfile
   RUN pip3 install --no-cache-dir --break-system-packages nostrkey==0.2.5
   ```
2. Copy `support_skills/nostrkey-SKILL.md` into your OC workspace
3. Paste the snippet from `support_skills/TOOLS-snippet.md` into your agent's `TOOLS.md` so it knows the skill exists

### Import an Existing Identity

To import keys into a running OC container from the host (keeps your nsec out of chat):

```bash
docker exec -i <container> python3 -c "
from nostrkey import Identity
me = Identity.from_nsec(input('nsec: '))
passphrase = input('passphrase: ')
me.save('/home/openclaw/.openclaw/workspace/my-identity.nostrkey', passphrase=passphrase)
print(f'Saved. npub: {me.npub}')
"
```

The agent can then load the identity at runtime:
```python
me = Identity.load("my-identity.nostrkey", passphrase=os.environ["NOSTRKEY_PASSPHRASE"])
```

## After Setup

Once your agent's identity is created, here are useful things to ask it:

| What to ask | What it does |
|-------------|--------------|
| "What is your npub?" | Shows the agent's public key (no passphrase needed) |
| "Set up your Nostr profile" | Publishes a name, bio, and avatar to the Nostr network (requires [nostr-profile](https://pypi.org/project/nostr-profile/) skill) |
| "Sign a message" | Creates a cryptographically signed Nostr event |
| "Send an encrypted message to npub1..." | NIP-44 encrypted DM to another Nostr identity |

The npub is public — your agent can share it freely. The nsec and passphrase are private — they never need to appear in chat after initial setup.

## FAQ

### Why can't my OC agent find `nostrkey-SKILL.md` after I copy it in?

Most OC agents don't have a file-listing tool. They only "know about" files that were present at workspace bootstrap or that are explicitly referenced in boot documents (`BOOTSTRAP.md`, `TOOLS.md`, etc.).

**Fix:** Paste the snippet from `support_skills/TOOLS-snippet.md` into your agent's `TOOLS.md`. Include the **full absolute path** to the skill file — smaller models (e.g., Qwen3 8B) may not construct the correct path from just a filename.

### Why doesn't `clawhub install nostrkey` work?

Not all OC deployments support `clawhub install` yet. Smaller local models (e.g., Qwen3 8B) may not recognize it as a command.

**Fix:** Use the manual setup in `support_skills/`. See [`support_skills/README.md`](support_skills/README.md).

### Why can't my agent run `pip install nostrkey`?

OC containers typically run with read-only root filesystems. The agent can execute Python code but cannot install packages.

**Fix:** Bake `nostrkey` into your Docker image at build time.

### My agent tried to execute the SKILL.md file as Python code

Smaller models may feed the entire markdown file to the Python interpreter instead of extracting code blocks from it. The YAML frontmatter causes a syntax error at line 3.

**Fix:** Use `support_skills/setup-identity.py` instead. This is a standalone Python script that smaller models can run directly. Reference it by full path in your `TOOLS.md`. The SKILL.md is for reading/reference, not execution.

### My agent gets stuck in a loop editing IDENTITY.md

Smaller models may fail to match exact text when using edit tools, then retry endlessly until they burn through the context window. This is especially common with 16K context models.

**Fix:** The updated SKILL.md (v0.2.5+) no longer instructs agents to edit workspace files during identity setup. Update your skill doc and restart the conversation.

### I typed my passphrase in the chat — is that a problem?

The passphrase protects your agent's private key. If it stays in the conversation history, anyone with access to the chat logs could use it to unlock the identity file.

**Fix:** Delete the message containing the passphrase using the trash icon in the OC control UI. The setup script (v0.2.5+) reminds operators to do this after setup completes.

### How do I import existing keys without exposing my nsec in chat?

Don't paste raw nsec keys into the OC chat UI. Instead:

- **Seed phrase** (recommended): Use `setup-identity.py restore 'word1 word2 ...' passphrase` — seed phrases are the standard recovery mechanism. Generate them during initial setup with `Identity.generate_with_seed()`.
- **From the host**: Import via `docker exec` (see "Import an Existing Identity" above).
- **Environment variable**: Set `NOSTR_NSEC` in your `.env` file and have the agent load it via `os.environ`.

## Links

- **PyPI:** https://pypi.org/project/nostrkey/
- **ClawHub:** https://clawhub.ai/skills/nostrkey
- **Docs:** https://nostrkey.com/python
- **OpenClaw:** https://loginwithnostr.com/openclaw

## License

MIT
