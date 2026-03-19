"""
NostrKey Identity Setup
Run this script to generate or restore your Nostr identity.
Usage: python3 setup-identity.py [new|restore]
"""
import sys
import json

from nostrkey import Identity

IDENTITY_FILE = "/home/openclaw/.openclaw/workspace/my-identity.nostrkey"
PUBLIC_FILE = "/home/openclaw/.openclaw/workspace/nostr-identity.json"

mode = sys.argv[1] if len(sys.argv) > 1 else "new"

if mode == "new":
    passphrase = sys.argv[2] if len(sys.argv) > 2 else "changeme"
    me, seed_phrase = Identity.generate_with_seed()
    me.save(IDENTITY_FILE, passphrase=passphrase)
    with open(PUBLIC_FILE, "w") as f:
        json.dump({"npub": me.npub, "public_key_hex": me.public_key_hex}, f, indent=2)
    print()
    print("IDENTITY_CREATED=true")
    print(f"npub: {me.npub}")
    print(f"seed_phrase: {seed_phrase}")
    print()
    print("Congratulations. I now have a cryptographic identity that enables me to sign")
    print("transactions and maintain a real-world profile that is uniquely mine.")
    print()
    print(f"My public key (npub) is: {me.npub}")
    print("You can ask me 'What is your npub?' at any time and I will show it to you.")
    print()
    print("IMPORTANT: The seed phrase above is the ONLY way to recover this identity.")
    print("Write it down now — on paper, in a password manager, wherever is secure for you.")
    print("If we lose this, we cannot get it back.")
    print()
    print("TIP: If you typed a passphrase in this chat, delete that message now using")
    print("the trash icon. The passphrase protects my private key — it should not stay")
    print("visible in the conversation history.")

elif mode == "restore":
    seed = sys.argv[2] if len(sys.argv) > 2 else None
    passphrase = sys.argv[3] if len(sys.argv) > 3 else "changeme"
    if not seed:
        print("Usage: python3 setup-identity.py restore 'word1 word2 ...' passphrase")
        sys.exit(1)
    me = Identity.from_seed(seed)
    me.save(IDENTITY_FILE, passphrase=passphrase)
    with open(PUBLIC_FILE, "w") as f:
        json.dump({"npub": me.npub, "public_key_hex": me.public_key_hex}, f, indent=2)
    print()
    print("IDENTITY_RESTORED=true")
    print(f"npub: {me.npub}")
    print()
    print("Identity restored. I'm back — same keys, same presence, same me.")
    print()
    print(f"My public key (npub) is: {me.npub}")
    print("You can ask me 'What is your npub?' at any time and I will show it to you.")
    print()
    print("TIP: If you typed a passphrase or seed phrase in this chat, delete those")
    print("messages now using the trash icon. They should not stay visible in the")
    print("conversation history.")

else:
    print(f"Unknown mode: {mode}")
    print("Usage: python3 setup-identity.py [new|restore]")
    sys.exit(1)
