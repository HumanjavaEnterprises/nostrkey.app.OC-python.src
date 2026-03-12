"""Quick start example — create an OpenClaw bot identity and sign an event."""

from nostrkey import Identity

# Generate a new identity for your bot
bot = Identity.generate()
print(f"Bot npub: {bot.npub}")
print(f"Bot nsec: {bot.nsec}")
print()

# Sign a text note (kind 1)
event = bot.sign_event(
    kind=1,
    content="Hello Nostr! I'm an OpenClaw bot with my own cryptographic identity.",
    tags=[["t", "openclaw"], ["t", "nostrkey"]],
)

print(f"Event ID: {event.id}")
print(f"Signed by: {event.pubkey}")
print(f"Signature: {event.sig[:32]}...")
print()

# Save the identity (encrypted with passphrase)
bot.save("my-bot.nostrkey", passphrase="demo-passphrase")
print("Identity saved to my-bot.nostrkey")

# Load it back
loaded = Identity.load("my-bot.nostrkey", passphrase="demo-passphrase")
print(f"Loaded npub: {loaded.npub}")
print(f"Keys match: {loaded.npub == bot.npub}")
