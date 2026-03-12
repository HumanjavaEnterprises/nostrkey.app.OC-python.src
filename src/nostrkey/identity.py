"""High-level OpenClaw identity management.

Provides a simple interface for creating, saving, loading, and using
a Nostr identity for AI entities.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
from dataclasses import dataclass

from nostrkey.events import NostrEvent, UnsignedEvent, sign_event
from nostrkey.keys import (
    generate_keypair,
    hex_to_npub,
    hex_to_nsec,
    nsec_to_hex,
    private_key_to_public_key,
)


@dataclass
class Identity:
    """A Nostr identity for an OpenClaw AI entity.

    Holds the keypair and provides methods for signing events,
    saving/loading identity files, and accessing key formats.
    """

    _private_key_hex: str
    _public_key_hex: str

    @classmethod
    def generate(cls) -> Identity:
        """Generate a new random identity."""
        privkey, pubkey = generate_keypair()
        return cls(_private_key_hex=privkey, _public_key_hex=pubkey)

    @classmethod
    def from_nsec(cls, nsec: str) -> Identity:
        """Create an identity from an existing nsec."""
        privkey_hex = nsec_to_hex(nsec)
        pubkey_hex = private_key_to_public_key(privkey_hex)
        return cls(_private_key_hex=privkey_hex, _public_key_hex=pubkey_hex)

    @classmethod
    def from_hex(cls, private_key_hex: str) -> Identity:
        """Create an identity from an existing hex private key."""
        pubkey_hex = private_key_to_public_key(private_key_hex)
        return cls(_private_key_hex=private_key_hex, _public_key_hex=pubkey_hex)

    @property
    def npub(self) -> str:
        """Public key in bech32 npub format."""
        return hex_to_npub(self._public_key_hex)

    @property
    def nsec(self) -> str:
        """Private key in bech32 nsec format."""
        return hex_to_nsec(self._private_key_hex)

    @property
    def public_key_hex(self) -> str:
        """Public key in hex format."""
        return self._public_key_hex

    @property
    def private_key_hex(self) -> str:
        """Private key in hex format."""
        return self._private_key_hex

    def sign_event(
        self, kind: int, content: str, tags: list[list[str]] | None = None
    ) -> NostrEvent:
        """Create and sign a Nostr event.

        Args:
            kind: Event kind (1 = text note, 0 = metadata, etc.).
            content: Event content string.
            tags: Optional list of tags.

        Returns:
            A signed NostrEvent ready for publishing.
        """
        unsigned = UnsignedEvent(kind=kind, content=content, tags=tags or [])
        return sign_event(self._private_key_hex, unsigned)

    def save(self, filepath: str, passphrase: str) -> None:
        """Save the identity to an encrypted file.

        Args:
            filepath: Path to save the identity file.
            passphrase: Passphrase to encrypt the private key.
        """
        salt = os.urandom(16)
        key = hashlib.pbkdf2_hmac("sha256", passphrase.encode(), salt, 100_000)

        # XOR encrypt the private key with the derived key
        privkey_bytes = bytes.fromhex(self._private_key_hex)
        encrypted = bytes(a ^ b for a, b in zip(privkey_bytes, key))

        data = {
            "version": 1,
            "npub": self.npub,
            "salt": base64.b64encode(salt).decode(),
            "encrypted_nsec": base64.b64encode(encrypted).decode(),
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, filepath: str, passphrase: str) -> Identity:
        """Load an identity from an encrypted file.

        Args:
            filepath: Path to the identity file.
            passphrase: Passphrase to decrypt the private key.

        Returns:
            The decrypted Identity.
        """
        with open(filepath) as f:
            data = json.load(f)

        if data.get("version") != 1:
            raise ValueError(f"Unsupported identity file version: {data.get('version')}")

        salt = base64.b64decode(data["salt"])
        encrypted = base64.b64decode(data["encrypted_nsec"])
        key = hashlib.pbkdf2_hmac("sha256", passphrase.encode(), salt, 100_000)

        privkey_bytes = bytes(a ^ b for a, b in zip(encrypted, key))
        return cls.from_hex(privkey_bytes.hex())

    def __repr__(self) -> str:
        return f"Identity(npub={self.npub[:20]}...)"

    def __str__(self) -> str:
        return self.npub
