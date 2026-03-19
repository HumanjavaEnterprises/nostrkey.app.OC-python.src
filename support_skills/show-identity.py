"""
NostrKey Identity Info
Run this to see your current Nostr public identity. No passphrase needed.
Usage: python3 show-identity.py
"""
import json
import sys

PUBLIC_FILE = "/home/openclaw/.openclaw/workspace/nostr-identity.json"

try:
    with open(PUBLIC_FILE) as f:
        identity = json.load(f)
    print(f"npub: {identity['npub']}")
    print(f"public_key_hex: {identity['public_key_hex']}")
except FileNotFoundError:
    print("No identity found. Run setup-identity.py first to create one.")
except Exception as e:
    print(f"Error: {e}")
