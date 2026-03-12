"""Tests for the Identity class."""

import os
import tempfile

from nostrkey.identity import Identity


def test_generate_identity():
    bot = Identity.generate()
    assert bot.npub.startswith("npub1")
    assert bot.nsec.startswith("nsec1")
    assert len(bot.public_key_hex) == 64
    assert len(bot.private_key_hex) == 64


def test_from_nsec():
    original = Identity.generate()
    restored = Identity.from_nsec(original.nsec)
    assert restored.npub == original.npub
    assert restored.nsec == original.nsec


def test_from_hex():
    original = Identity.generate()
    restored = Identity.from_hex(original.private_key_hex)
    assert restored.npub == original.npub


def test_sign_event():
    bot = Identity.generate()
    event = bot.sign_event(kind=1, content="hello from bot")
    assert event.pubkey == bot.public_key_hex
    assert event.content == "hello from bot"


def test_save_and_load():
    bot = Identity.generate()
    passphrase = "test-passphrase-123"

    with tempfile.NamedTemporaryFile(suffix=".nostrkey", delete=False) as f:
        filepath = f.name

    try:
        bot.save(filepath, passphrase)
        loaded = Identity.load(filepath, passphrase)
        assert loaded.npub == bot.npub
        assert loaded.nsec == bot.nsec
    finally:
        os.unlink(filepath)


def test_repr():
    bot = Identity.generate()
    assert "Identity(npub=" in repr(bot)
    assert str(bot).startswith("npub1")
