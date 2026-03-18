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


def test_backup_card():
    bot = Identity.generate()
    card = bot.backup_card()
    assert card["npub"].startswith("npub1")
    assert card["nsec"].startswith("nsec1")
    assert len(card["public_key_hex"]) == 64
    assert "warning" in card


def test_export_and_restore_token():
    bot = Identity.generate()
    passphrase = "my-secret-phrase"
    token = bot.export_token(passphrase)

    assert token.startswith("nostrkey:v3:")

    restored = Identity.from_token(token, passphrase)
    assert restored.npub == bot.npub
    assert restored.nsec == bot.nsec


def test_token_wrong_passphrase():
    bot = Identity.generate()
    token = bot.export_token("correct-passphrase")

    try:
        Identity.from_token(token, "wrong-passphrase")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Invalid passphrase" in str(e)


def test_token_invalid_format():
    try:
        Identity.from_token("garbage", "passphrase")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Invalid token format" in str(e)


def test_token_empty_passphrase():
    bot = Identity.generate()
    try:
        bot.export_token("")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "empty" in str(e).lower()


def test_token_roundtrip_different_identities():
    """Two different identities produce different tokens."""
    bot1 = Identity.generate()
    bot2 = Identity.generate()
    passphrase = "same-passphrase"

    token1 = bot1.export_token(passphrase)
    token2 = bot2.export_token(passphrase)

    assert token1 != token2

    restored1 = Identity.from_token(token1, passphrase)
    restored2 = Identity.from_token(token2, passphrase)

    assert restored1.npub == bot1.npub
    assert restored2.npub == bot2.npub
    assert restored1.npub != restored2.npub
