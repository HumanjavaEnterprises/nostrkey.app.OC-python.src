"""High-level OpenClaw identity management.

Provides a simple interface for creating, saving, loading, and using
a Nostr identity for AI entities.
"""

from __future__ import annotations

import base64
import hashlib
import hmac as hmac_module
import json
import os
import secrets
from dataclasses import dataclass, field

from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

from nostrkey.events import NostrEvent, UnsignedEvent, sign_event
from nostrkey.keys import (
    _validate_hex_key,
    _validate_private_key,
    generate_keypair,
    hex_to_npub,
    hex_to_nsec,
    nsec_to_hex,
    private_key_to_public_key,
)


def _validate_path(filepath: str) -> str:
    """Resolve and validate a file path against path traversal attacks."""
    resolved = os.path.realpath(filepath)
    if ".." in resolved:
        raise ValueError(f"Invalid path: path traversal detected in {filepath!r}")
    return resolved


@dataclass
class Identity:
    """A Nostr identity for an OpenClaw AI entity.

    Holds the keypair and provides methods for signing events,
    saving/loading identity files, and accessing key formats.
    """

    _private_key_hex: str = field(repr=False)
    _public_key_hex: str = field(repr=False)

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
        _validate_private_key(private_key_hex)
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

        Uses PBKDF2 key derivation and ChaCha20-Poly1305 AEAD encryption.

        Args:
            filepath: Path to save the identity file.
            passphrase: Passphrase to encrypt the private key.
        """
        filepath = _validate_path(filepath)
        salt = secrets.token_bytes(16)
        key = hashlib.pbkdf2_hmac("sha256", passphrase.encode(), salt, 600_000)
        nonce = secrets.token_bytes(12)

        privkey_bytes = bytes.fromhex(self._private_key_hex)
        aead = ChaCha20Poly1305(key)
        encrypted = aead.encrypt(nonce, privkey_bytes, salt)

        data = {
            "version": 3,
            "npub": self.npub,
            "salt": base64.b64encode(salt).decode(),
            "nonce": base64.b64encode(nonce).decode(),
            "encrypted_nsec": base64.b64encode(encrypted).decode(),
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, filepath: str, passphrase: str) -> Identity:
        """Load an identity from an encrypted file.

        Supports version 1 (XOR, no auth), version 2 (XOR + HMAC),
        and version 3 (ChaCha20-Poly1305 AEAD).

        Args:
            filepath: Path to the identity file.
            passphrase: Passphrase to decrypt the private key.

        Returns:
            The decrypted Identity.

        Raises:
            ValueError: If the passphrase is wrong or the file is corrupted.
        """
        filepath = _validate_path(filepath)
        with open(filepath) as f:
            data = json.load(f)

        version = data.get("version")
        if version not in (2, 3):
            if version == 1:
                raise ValueError(
                    "Version 1 identity files are no longer supported — re-save with a current version"
                )
            raise ValueError(f"Unsupported identity file version: {version}")

        salt = base64.b64decode(data["salt"])
        encrypted = base64.b64decode(data["encrypted_nsec"])

        if version == 3:
            key = hashlib.pbkdf2_hmac("sha256", passphrase.encode(), salt, 600_000)
            nonce = base64.b64decode(data["nonce"])
            aead = ChaCha20Poly1305(key)
            try:
                privkey_bytes = aead.decrypt(nonce, encrypted, salt)
            except Exception:
                raise ValueError("Invalid passphrase or corrupted file")
            return cls.from_hex(privkey_bytes.hex())

        # Legacy v2 support
        key = hashlib.pbkdf2_hmac("sha256", passphrase.encode(), salt, 600_000)
        stored_mac = base64.b64decode(data["hmac"])
        expected_mac = hmac_module.new(key, salt + encrypted, hashlib.sha256).digest()
        if not hmac_module.compare_digest(stored_mac, expected_mac):
            raise ValueError("Invalid passphrase or corrupted file")

        privkey_bytes = bytes(a ^ b for a, b in zip(encrypted, key))
        return cls.from_hex(privkey_bytes.hex())

    def wipe(self) -> None:
        """Best-effort zeroing of private key material from memory.

        Call this when the identity is no longer needed. Note: CPython
        string interning means this cannot guarantee full erasure, but
        it removes the direct references.
        """
        self._private_key_hex = "0" * 64
        self._public_key_hex = "0" * 64

    def __del__(self) -> None:
        try:
            self.wipe()
        except Exception:
            pass

    def __repr__(self) -> str:
        return f"Identity(npub={self.npub[:20]}...)"

    def __str__(self) -> str:
        return self.npub
