"""Key generation and bech32 encoding/decoding for Nostr (NIP-19)."""

from __future__ import annotations

import os

import bech32
import secp256k1


def generate_keypair() -> tuple[str, str]:
    """Generate a new Nostr keypair.

    Returns:
        Tuple of (private_key_hex, public_key_hex).
    """
    private_key_bytes = os.urandom(32)
    privkey = secp256k1.PrivateKey(private_key_bytes)
    public_key_bytes = privkey.pubkey.serialize(compressed=True)[1:]  # x-only pubkey
    return private_key_bytes.hex(), public_key_bytes.hex()


def hex_to_nsec(private_key_hex: str) -> str:
    """Convert a hex private key to bech32 nsec format."""
    return _bech32_encode("nsec", bytes.fromhex(private_key_hex))


def hex_to_npub(public_key_hex: str) -> str:
    """Convert a hex public key to bech32 npub format."""
    return _bech32_encode("npub", bytes.fromhex(public_key_hex))


def nsec_to_hex(nsec: str) -> str:
    """Convert a bech32 nsec to hex private key."""
    return _bech32_decode("nsec", nsec).hex()


def npub_to_hex(npub: str) -> str:
    """Convert a bech32 npub to hex public key."""
    return _bech32_decode("npub", npub).hex()


def private_key_to_public_key(private_key_hex: str) -> str:
    """Derive the public key from a private key."""
    privkey = secp256k1.PrivateKey(bytes.fromhex(private_key_hex))
    return privkey.pubkey.serialize(compressed=True)[1:].hex()


def _bech32_encode(hrp: str, data: bytes) -> str:
    """Encode bytes to bech32."""
    converted = bech32.convertbits(list(data), 8, 5, True)
    if converted is None:
        raise ValueError("Failed to convert bits for bech32 encoding")
    return bech32.bech32_encode(hrp, converted)


def _bech32_decode(expected_hrp: str, bech32_str: str) -> bytes:
    """Decode bech32 string to bytes."""
    hrp, data = bech32.bech32_decode(bech32_str)
    if hrp != expected_hrp:
        raise ValueError(f"Expected hrp '{expected_hrp}', got '{hrp}'")
    if data is None:
        raise ValueError("Failed to decode bech32 string")
    converted = bech32.convertbits(data, 5, 8, False)
    if converted is None:
        raise ValueError("Failed to convert bits from bech32")
    return bytes(converted)
