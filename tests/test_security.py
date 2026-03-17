"""Tests for security hardening — relay validation, key validation, identity edge cases."""

import os
import tempfile

import pytest

from nostrkey import Identity
from nostrkey.keys import _validate_private_key
from nostrkey.relay import validate_relay_url


class TestRelayValidation:
    """SSRF prevention tests for validate_relay_url."""

    def test_valid_wss(self):
        validate_relay_url("wss://relay.damus.io")

    def test_valid_ws(self):
        validate_relay_url("ws://relay.example.com")

    def test_rejects_http(self):
        with pytest.raises(ValueError, match="scheme"):
            validate_relay_url("http://relay.example.com")

    def test_rejects_localhost(self):
        with pytest.raises(ValueError, match="localhost"):
            validate_relay_url("wss://localhost")

    def test_rejects_zero_address(self):
        with pytest.raises(ValueError, match="localhost"):
            validate_relay_url("wss://0.0.0.0")

    def test_rejects_loopback(self):
        with pytest.raises(ValueError, match="private"):
            validate_relay_url("wss://127.0.0.1")

    def test_rejects_private_10(self):
        with pytest.raises(ValueError, match="private"):
            validate_relay_url("wss://10.0.0.1")

    def test_rejects_private_192(self):
        with pytest.raises(ValueError, match="private"):
            validate_relay_url("wss://192.168.1.1")

    def test_rejects_private_172(self):
        with pytest.raises(ValueError, match="private"):
            validate_relay_url("wss://172.16.0.1")

    def test_rejects_ipv6_loopback(self):
        with pytest.raises(ValueError, match="private"):
            validate_relay_url("wss://[::1]")

    def test_rejects_no_hostname(self):
        with pytest.raises(ValueError):
            validate_relay_url("wss://")


class TestKeyValidation:
    """Private key range validation tests."""

    def test_zero_key_rejected(self):
        with pytest.raises(ValueError, match="range"):
            _validate_private_key("0" * 64)

    def test_key_at_curve_order_rejected(self):
        n_hex = format(
            0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141, "064x"
        )
        with pytest.raises(ValueError, match="range"):
            _validate_private_key(n_hex)

    def test_key_above_curve_order_rejected(self):
        above_n = format(
            0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364142, "064x"
        )
        with pytest.raises(ValueError, match="range"):
            _validate_private_key(above_n)

    def test_valid_key_passes(self):
        _validate_private_key("0" * 63 + "1")  # key = 1, smallest valid

    def test_short_key_rejected(self):
        with pytest.raises(ValueError, match="64 hex"):
            _validate_private_key("abcd")

    def test_non_hex_rejected(self):
        with pytest.raises(ValueError, match="64 hex"):
            _validate_private_key("g" * 64)


class TestIdentitySecurity:
    """Identity save/load security tests."""

    def test_wrong_passphrase_rejected(self):
        bot = Identity.generate()
        with tempfile.NamedTemporaryFile(suffix=".nostrkey", delete=False) as f:
            path = f.name
        try:
            bot.save(path, "correct-password")
            with pytest.raises(ValueError, match="Invalid passphrase"):
                Identity.load(path, "wrong-password")
        finally:
            os.unlink(path)

    def test_save_load_roundtrip_v3(self):
        bot = Identity.generate()
        with tempfile.NamedTemporaryFile(suffix=".nostrkey", delete=False) as f:
            path = f.name
        try:
            bot.save(path, "test-pass")
            loaded = Identity.load(path, "test-pass")
            assert loaded.npub == bot.npub
            assert loaded.private_key_hex == bot.private_key_hex
        finally:
            os.unlink(path)

    def test_wipe_clears_key(self):
        bot = Identity.generate()
        original_npub = bot.npub
        bot.wipe()
        assert bot._private_key_hex == "0" * 64
        assert bot._public_key_hex == "0" * 64

    def test_repr_does_not_expose_private_key(self):
        bot = Identity.generate()
        r = repr(bot)
        assert bot._private_key_hex not in r
        assert "nsec" not in r
