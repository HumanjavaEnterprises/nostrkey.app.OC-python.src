"""Tests for BIP-39 seed phrase support (NIP-06)."""

import pytest

from nostrkey.identity import Identity
from nostrkey.seed import generate_seed_phrase, validate_seed_phrase, seed_phrase_to_private_key


def test_generate_seed_phrase_12_words():
    phrase = generate_seed_phrase(128)
    words = phrase.split()
    assert len(words) == 12


def test_generate_seed_phrase_24_words():
    phrase = generate_seed_phrase(256)
    words = phrase.split()
    assert len(words) == 24


def test_generate_seed_phrase_invalid_strength():
    with pytest.raises(ValueError, match="128.*256"):
        generate_seed_phrase(64)


def test_validate_seed_phrase_valid():
    phrase = generate_seed_phrase()
    assert validate_seed_phrase(phrase) is True


def test_validate_seed_phrase_invalid():
    assert validate_seed_phrase("not a valid seed phrase at all") is False
    assert validate_seed_phrase("") is False
    assert validate_seed_phrase(None) is False


def test_seed_phrase_to_private_key():
    phrase = generate_seed_phrase()
    privkey = seed_phrase_to_private_key(phrase)
    assert len(privkey) == 64  # hex string
    assert all(c in "0123456789abcdef" for c in privkey)


def test_seed_phrase_deterministic():
    """Same seed phrase always produces the same key."""
    phrase = generate_seed_phrase()
    key1 = seed_phrase_to_private_key(phrase)
    key2 = seed_phrase_to_private_key(phrase)
    assert key1 == key2


def test_different_phrases_different_keys():
    phrase1 = generate_seed_phrase()
    phrase2 = generate_seed_phrase()
    key1 = seed_phrase_to_private_key(phrase1)
    key2 = seed_phrase_to_private_key(phrase2)
    assert key1 != key2


def test_seed_phrase_invalid_raises():
    with pytest.raises(ValueError, match="Invalid BIP-39"):
        seed_phrase_to_private_key("invalid words here")


def test_identity_generate_with_seed():
    identity, phrase = Identity.generate_with_seed()
    assert identity.npub.startswith("npub1")
    assert identity.nsec.startswith("nsec1")
    words = phrase.split()
    assert len(words) == 12
    assert validate_seed_phrase(phrase) is True


def test_identity_generate_with_seed_24():
    identity, phrase = Identity.generate_with_seed(strength=256)
    words = phrase.split()
    assert len(words) == 24


def test_identity_from_seed():
    identity, phrase = Identity.generate_with_seed()
    restored = Identity.from_seed(phrase)
    assert restored.npub == identity.npub
    assert restored.nsec == identity.nsec


def test_identity_from_seed_invalid():
    with pytest.raises(ValueError):
        Identity.from_seed("not valid words")


def test_seed_roundtrip_with_token():
    """Seed phrase and token backup can both restore the same identity."""
    identity, phrase = Identity.generate_with_seed()
    token = identity.export_token("test-pass")

    from_seed = Identity.from_seed(phrase)
    from_token = Identity.from_token(token, "test-pass")

    assert from_seed.npub == identity.npub
    assert from_token.npub == identity.npub
    assert from_seed.npub == from_token.npub
