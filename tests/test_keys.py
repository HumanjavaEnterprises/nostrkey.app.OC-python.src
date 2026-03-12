"""Tests for key generation and bech32 encoding."""

from nostrkey.keys import (
    generate_keypair,
    hex_to_npub,
    hex_to_nsec,
    npub_to_hex,
    nsec_to_hex,
    private_key_to_public_key,
)


def test_generate_keypair():
    privkey, pubkey = generate_keypair()
    assert len(privkey) == 64  # 32 bytes hex
    assert len(pubkey) == 64


def test_keypair_is_unique():
    pair1 = generate_keypair()
    pair2 = generate_keypair()
    assert pair1[0] != pair2[0]
    assert pair1[1] != pair2[1]


def test_bech32_roundtrip_nsec():
    privkey, _ = generate_keypair()
    nsec = hex_to_nsec(privkey)
    assert nsec.startswith("nsec1")
    assert nsec_to_hex(nsec) == privkey


def test_bech32_roundtrip_npub():
    _, pubkey = generate_keypair()
    npub = hex_to_npub(pubkey)
    assert npub.startswith("npub1")
    assert npub_to_hex(npub) == pubkey


def test_private_key_to_public_key():
    privkey, pubkey = generate_keypair()
    derived = private_key_to_public_key(privkey)
    assert derived == pubkey
