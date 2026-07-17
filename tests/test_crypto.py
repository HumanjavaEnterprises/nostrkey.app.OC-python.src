"""Tests for NIP-44 encryption/decryption and padding."""

import pytest

from nostrkey import Identity
from nostrkey.crypto import _calc_padded_len, _pad_plaintext, _unpad_plaintext, encrypt, decrypt


class TestNIP44Padding:
    """Verify the NIP-44 padding algorithm matches the spec."""

    def test_short_messages_pad_to_32(self):
        for length in (1, 15, 31, 32):
            assert _calc_padded_len(length) == 32

    def test_33_pads_to_64(self):
        assert _calc_padded_len(33) == 64

    def test_65_pads_to_96(self):
        assert _calc_padded_len(65) == 96

    def test_257_pads_to_320(self):
        assert _calc_padded_len(257) == 320

    def test_zero_length_raises(self):
        with pytest.raises(ValueError):
            _calc_padded_len(0)

    def test_pad_unpad_roundtrip(self):
        for msg in (b"a", b"x" * 32, b"y" * 33, b"z" * 256, b"w" * 1000):
            padded = _pad_plaintext(msg)
            assert _unpad_plaintext(padded) == msg

    def test_pad_too_long_raises(self):
        with pytest.raises(ValueError):
            _pad_plaintext(b"x" * 65536)


class TestNIP44UnpadValidation:
    """Malformed padding must be rejected, not silently accepted (NIP-44 v2)."""

    def test_declared_length_zero_raises(self):
        # 2-byte prefix declaring length 0 followed by a valid 32-byte block
        padded = b"\x00\x00" + b"\x00" * 32
        with pytest.raises(ValueError):
            _unpad_plaintext(padded)

    def test_declared_length_exceeds_buffer_raises(self):
        # Declares 100 bytes of plaintext but only 32 bytes follow
        padded = b"\x00\x64" + b"a" * 32
        with pytest.raises(ValueError):
            _unpad_plaintext(padded)

    def test_oversized_padding_raises(self):
        # Declares 5 bytes (canonical padded length 32, total 34) but the
        # buffer carries 64 bytes of padded content — inconsistent padding
        padded = b"\x00\x05" + b"hello" + b"\x00" * 59
        with pytest.raises(ValueError):
            _unpad_plaintext(padded)

    def test_undersized_padding_raises(self):
        # Declares 33 bytes (canonical padded length 64, total 66) but the
        # buffer only carries 40 bytes of padded content
        padded = b"\x00\x21" + b"x" * 33 + b"\x00" * 5
        with pytest.raises(ValueError):
            _unpad_plaintext(padded)

    def test_truncated_buffer_raises(self):
        with pytest.raises(ValueError):
            _unpad_plaintext(b"\x00")

    def test_canonical_padding_accepted(self):
        assert _unpad_plaintext(_pad_plaintext(b"hello")) == b"hello"


class TestNIP44EncryptDecrypt:
    """Test encrypt/decrypt roundtrip."""

    def test_roundtrip(self):
        alice = Identity.generate()
        bob = Identity.generate()

        plaintext = "Hello from Alice to Bob!"
        ciphertext = encrypt(alice.private_key_hex, bob.public_key_hex, plaintext)
        decrypted = decrypt(bob.private_key_hex, alice.public_key_hex, ciphertext)
        assert decrypted == plaintext

    def test_roundtrip_with_bech32(self):
        alice = Identity.generate()
        bob = Identity.generate()

        ciphertext = encrypt(alice.nsec, bob.npub, "bech32 test")
        decrypted = decrypt(bob.nsec, alice.npub, ciphertext)
        assert decrypted == "bech32 test"

    def test_wrong_key_fails(self):
        alice = Identity.generate()
        bob = Identity.generate()
        eve = Identity.generate()

        ciphertext = encrypt(alice.private_key_hex, bob.public_key_hex, "secret")
        with pytest.raises(ValueError, match="HMAC"):
            decrypt(eve.private_key_hex, alice.public_key_hex, ciphertext)

    def test_empty_plaintext_raises(self):
        alice = Identity.generate()
        bob = Identity.generate()
        with pytest.raises(ValueError, match="empty"):
            encrypt(alice.private_key_hex, bob.public_key_hex, "")

    def test_short_ciphertext_raises(self):
        alice = Identity.generate()
        bob = Identity.generate()
        import base64
        short = base64.b64encode(b"\x02" + b"\x00" * 10).decode()
        with pytest.raises(ValueError, match="too short"):
            decrypt(alice.private_key_hex, bob.public_key_hex, short)
