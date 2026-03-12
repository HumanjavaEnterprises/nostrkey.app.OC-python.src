"""NostrKey — Nostr identity SDK for OpenClaw AI entities."""

from nostrkey.identity import Identity
from nostrkey.keys import generate_keypair, nsec_to_hex, npub_to_hex, hex_to_nsec, hex_to_npub

__version__ = "0.1.1"
__all__ = [
    "Identity",
    "generate_keypair",
    "nsec_to_hex",
    "npub_to_hex",
    "hex_to_nsec",
    "hex_to_npub",
]
