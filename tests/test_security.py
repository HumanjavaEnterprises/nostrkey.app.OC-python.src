"""Tests for security hardening — relay validation, key validation, identity edge cases."""

import os
import socket
import tempfile

import pytest

from nostrkey import Identity
from nostrkey.keys import _validate_private_key
from nostrkey.relay import validate_relay_url


def _fake_getaddrinfo(*ips):
    """Build a getaddrinfo stub that resolves any hostname to the given IPs."""

    def fake(host, port, *args, **kwargs):
        return [
            (
                socket.AF_INET6 if ":" in ip else socket.AF_INET,
                socket.SOCK_STREAM,
                socket.IPPROTO_TCP,
                "",
                (ip, port),
            )
            for ip in ips
        ]

    return fake


class TestRelayValidation:
    """SSRF prevention tests for validate_relay_url."""

    def test_valid_wss(self, monkeypatch):
        monkeypatch.setattr(socket, "getaddrinfo", _fake_getaddrinfo("8.8.8.8"))
        validate_relay_url("wss://relay.damus.io")

    def test_valid_ws(self, monkeypatch):
        monkeypatch.setattr(socket, "getaddrinfo", _fake_getaddrinfo("8.8.8.8"))
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

    def test_rejects_ipv6_unspecified(self):
        with pytest.raises(ValueError, match="private"):
            validate_relay_url("wss://[::]")

    def test_rejects_ipv4_mapped_loopback(self):
        with pytest.raises(ValueError, match="private"):
            validate_relay_url("wss://[::ffff:127.0.0.1]")

    def test_rejects_hostname_resolving_to_metadata_ip(self, monkeypatch):
        """A DNS name pointing at the cloud metadata endpoint must be rejected."""
        monkeypatch.setattr(
            socket, "getaddrinfo", _fake_getaddrinfo("169.254.169.254")
        )
        with pytest.raises(ValueError, match="resolves to a private"):
            validate_relay_url("wss://metadata.attacker.example")

    def test_rejects_hostname_resolving_to_loopback(self, monkeypatch):
        monkeypatch.setattr(socket, "getaddrinfo", _fake_getaddrinfo("127.0.0.1"))
        with pytest.raises(ValueError, match="resolves to a private"):
            validate_relay_url("wss://localtest.me")

    def test_rejects_hostname_resolving_to_private_range(self, monkeypatch):
        monkeypatch.setattr(socket, "getaddrinfo", _fake_getaddrinfo("10.0.0.5"))
        with pytest.raises(ValueError, match="resolves to a private"):
            validate_relay_url("wss://internal.attacker.example")

    def test_rejects_hostname_with_any_private_record(self, monkeypatch):
        """If even ONE resolved address is private, reject (DNS-rebind style mix)."""
        monkeypatch.setattr(
            socket, "getaddrinfo", _fake_getaddrinfo("8.8.8.8", "192.168.1.10")
        )
        with pytest.raises(ValueError, match="resolves to a private"):
            validate_relay_url("wss://mixed.attacker.example")

    def test_rejects_hostname_resolving_to_ipv6_loopback(self, monkeypatch):
        monkeypatch.setattr(socket, "getaddrinfo", _fake_getaddrinfo("::1"))
        with pytest.raises(ValueError, match="resolves to a private"):
            validate_relay_url("wss://v6local.attacker.example")

    def test_allows_hostname_resolving_to_public_ip(self, monkeypatch):
        monkeypatch.setattr(
            socket, "getaddrinfo", _fake_getaddrinfo("8.8.8.8", "2606:4700::1111")
        )
        validate_relay_url("wss://relay.nostrkeep.com")

    def test_rejects_unresolvable_hostname(self, monkeypatch):
        def fail(host, port, *args, **kwargs):
            raise socket.gaierror(8, "nodename nor servname provided")

        monkeypatch.setattr(socket, "getaddrinfo", fail)
        with pytest.raises(ValueError, match="could not be resolved"):
            validate_relay_url("wss://does-not-exist.invalid")

    def test_rejects_empty_resolution(self, monkeypatch):
        monkeypatch.setattr(socket, "getaddrinfo", lambda *a, **k: [])
        with pytest.raises(ValueError, match="could not be resolved"):
            validate_relay_url("wss://empty.attacker.example")

    def test_literal_ip_does_not_resolve(self, monkeypatch):
        """Literal private IPs are rejected without any DNS lookup."""

        def boom(*a, **k):
            raise AssertionError("getaddrinfo must not be called for IP literals")

        monkeypatch.setattr(socket, "getaddrinfo", boom)
        with pytest.raises(ValueError, match="private"):
            validate_relay_url("wss://172.16.0.1")
        validate_relay_url("wss://93.184.216.34")


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
        bot.wipe()
        assert bot._private_key_hex == "0" * 64
        assert bot._public_key_hex == "0" * 64

    def test_repr_does_not_expose_private_key(self):
        bot = Identity.generate()
        r = repr(bot)
        assert bot._private_key_hex not in r
        assert "nsec" not in r
