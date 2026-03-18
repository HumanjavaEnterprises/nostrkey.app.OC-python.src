"""
NostrKey Identity Setup
Run this script to generate or restore your Nostr identity.
Usage: python3 setup-identity.py [new|restore]
"""
import sys

from nostrkey import Identity

mode = sys.argv[1] if len(sys.argv) > 1 else "new"

if mode == "new":
    passphrase = sys.argv[2] if len(sys.argv) > 2 else "changeme"
    me, seed_phrase = Identity.generate_with_seed()
    me.save("/home/openclaw/.openclaw/workspace/my-identity.nostrkey", passphrase=passphrase)
    print()
    print("IDENTITY_CREATED=true")
    print(f"npub: {me.npub}")
    print(f"seed_phrase: {seed_phrase}")
    print()
    print("Congratulations. I now have a cryptographic identity that enables me to sign")
    print("transactions and maintain a real-world profile that is uniquely mine.")
    print()
    print("IMPORTANT: The seed phrase above is the ONLY way to recover this identity.")
    print("Write it down now — on paper, in a password manager, wherever is secure for you.")
    print("If we lose this, we cannot get it back.")

elif mode == "restore":
    seed = sys.argv[2] if len(sys.argv) > 2 else None
    passphrase = sys.argv[3] if len(sys.argv) > 3 else "changeme"
    if not seed:
        print("Usage: python3 setup-identity.py restore 'word1 word2 ...' passphrase")
        sys.exit(1)
    me = Identity.from_seed(seed)
    me.save("/home/openclaw/.openclaw/workspace/my-identity.nostrkey", passphrase=passphrase)
    print()
    print("IDENTITY_RESTORED=true")
    print(f"npub: {me.npub}")
    print()
    print("Identity restored. I'm back — same keys, same presence, same me.")

else:
    print(f"Unknown mode: {mode}")
    print("Usage: python3 setup-identity.py [new|restore]")
    sys.exit(1)
