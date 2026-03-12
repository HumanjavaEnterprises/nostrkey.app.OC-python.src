"""Tests for event creation and signing."""

from nostrkey.events import UnsignedEvent, sign_event, verify_event
from nostrkey.keys import generate_keypair


def test_sign_event():
    privkey, pubkey = generate_keypair()
    unsigned = UnsignedEvent(kind=1, content="test message", tags=[])
    event = sign_event(privkey, unsigned)

    assert event.pubkey == pubkey
    assert event.kind == 1
    assert event.content == "test message"
    assert len(event.id) == 64
    assert len(event.sig) == 128


def test_verify_event():
    privkey, _ = generate_keypair()
    unsigned = UnsignedEvent(kind=1, content="verify me", tags=[["t", "test"]])
    event = sign_event(privkey, unsigned)

    assert verify_event(event) is True


def test_verify_tampered_event():
    privkey, _ = generate_keypair()
    unsigned = UnsignedEvent(kind=1, content="original", tags=[])
    event = sign_event(privkey, unsigned)

    # Tamper with the content
    event.content = "tampered"
    assert verify_event(event) is False


def test_event_with_tags():
    privkey, _ = generate_keypair()
    tags = [["p", "npub1abc"], ["e", "event123"], ["t", "openclaw"]]
    unsigned = UnsignedEvent(kind=1, content="tagged", tags=tags)
    event = sign_event(privkey, unsigned)

    assert event.tags == tags
    assert verify_event(event) is True


def test_event_to_dict():
    privkey, pubkey = generate_keypair()
    event = sign_event(privkey, UnsignedEvent(kind=1, content="test"))
    d = event.to_dict()

    assert d["pubkey"] == pubkey
    assert d["kind"] == 1
    assert d["content"] == "test"
    assert "id" in d
    assert "sig" in d
    assert "created_at" in d
