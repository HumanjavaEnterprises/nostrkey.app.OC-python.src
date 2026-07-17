"""Tests for the NIP-46 bunker client (connect flow, normalization, timeout)."""

import asyncio
import json
import socket

import pytest

import nostrkey.bunker as bunker_module
from nostrkey.bunker import BunkerClient
from nostrkey.crypto import decrypt, encrypt
from nostrkey.events import UnsignedEvent, sign_event
from nostrkey.keys import generate_keypair, hex_to_npub

RELAY = "wss://relay.example.com"


@pytest.fixture(autouse=True)
def _public_dns(monkeypatch):
    """Resolve the fake test relay hostname to a public IP (no real DNS).

    validate_relay_url now resolves DNS hostnames and fails closed, so the
    fake relay hostname must appear to resolve publicly for these tests.
    """
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda host, port, *a, **k: [
            (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", ("8.8.8.8", port))
        ],
    )


class FakeWebSocket:
    """Minimal fake relay websocket.

    Records everything the client sends and lets a responder callable queue
    raw relay messages back to the client. With no responder, the client
    never receives a response (used for the timeout test).
    """

    def __init__(self, responder=None):
        self.sent = []
        self.responder = responder
        self.closed = False
        self._queue = asyncio.Queue()

    async def send(self, msg):
        self.sent.append(msg)
        if self.responder:
            for raw in self.responder(self, msg):
                self._queue.put_nowait(raw)

    def __aiter__(self):
        return self

    async def __anext__(self):
        return await self._queue.get()

    async def close(self):
        self.closed = True


def make_signer_responder(remote_privkey, remote_pubkey, result=None, error=None):
    """Build a responder that decrypts NIP-46 requests and answers them."""
    state = {"sub_id": None, "requests": []}

    def responder(ws, msg):
        data = json.loads(msg)
        if data[0] == "REQ":
            state["sub_id"] = data[1]
            return []
        if data[0] == "EVENT":
            evt = data[1]
            request = json.loads(decrypt(remote_privkey, evt["pubkey"], evt["content"]))
            state["requests"].append(request)
            response = {"id": request["id"]}
            if error is not None:
                response["error"] = error
            else:
                response["result"] = "ack" if result is None else result
            ciphertext = encrypt(remote_privkey, evt["pubkey"], json.dumps(response))
            signed = sign_event(
                remote_privkey,
                UnsignedEvent(kind=24133, content=ciphertext, tags=[["p", evt["pubkey"]]]),
            )
            return [json.dumps(["EVENT", state["sub_id"], signed.to_dict()])]
        return []

    responder.state = state
    return responder


def patch_ws(monkeypatch, fake_ws):
    async def fake_connect(url, **kwargs):
        fake_ws.url = url
        return fake_ws

    monkeypatch.setattr(bunker_module.websockets, "connect", fake_connect)


async def test_connect_npub_url_normalized_to_hex(monkeypatch):
    """npub-form bunker URLs must be normalized to hex everywhere."""
    remote_priv, remote_pub = generate_keypair()
    client_priv, client_pub = generate_keypair()
    responder = make_signer_responder(remote_priv, remote_pub)
    ws = FakeWebSocket(responder)
    patch_ws(monkeypatch, ws)

    client = BunkerClient(client_priv)
    await client.connect(f"bunker://{hex_to_npub(remote_pub)}?relay={RELAY}")

    assert client._remote_pubkey == remote_pub

    # The REQ authors filter and the request p-tag must both use hex
    req = json.loads(ws.sent[0])
    assert req[0] == "REQ"
    assert req[2]["authors"] == [remote_pub]
    assert req[2]["#p"] == [client_pub]
    evt = json.loads(ws.sent[1])[1]
    assert ["p", remote_pub] in evt["tags"]


async def test_connect_hex_url_still_works(monkeypatch):
    remote_priv, remote_pub = generate_keypair()
    client_priv, _ = generate_keypair()
    ws = FakeWebSocket(make_signer_responder(remote_priv, remote_pub))
    patch_ws(monkeypatch, ws)

    client = BunkerClient(client_priv)
    await client.connect(f"bunker://{remote_pub}?relay={RELAY}")
    assert client._remote_pubkey == remote_pub


async def test_connect_params_are_remote_pubkey_and_secret(monkeypatch):
    """NIP-46: connect params = [remote-signer-pubkey, optional-secret]."""
    remote_priv, remote_pub = generate_keypair()
    client_priv, _ = generate_keypair()
    responder = make_signer_responder(remote_priv, remote_pub)
    ws = FakeWebSocket(responder)
    patch_ws(monkeypatch, ws)

    client = BunkerClient(client_priv)
    await client.connect(f"bunker://{remote_pub}?relay={RELAY}&secret=s3cret")

    request = responder.state["requests"][0]
    assert request["method"] == "connect"
    assert request["params"] == [remote_pub, "s3cret"]


async def test_connect_without_secret_sends_empty_string(monkeypatch):
    remote_priv, remote_pub = generate_keypair()
    client_priv, _ = generate_keypair()
    responder = make_signer_responder(remote_priv, remote_pub)
    ws = FakeWebSocket(responder)
    patch_ws(monkeypatch, ws)

    client = BunkerClient(client_priv)
    await client.connect(f"bunker://{remote_pub}?relay={RELAY}")

    request = responder.state["requests"][0]
    assert request["params"] == [remote_pub, ""]


async def test_connect_accepts_echoed_secret_result(monkeypatch):
    remote_priv, remote_pub = generate_keypair()
    client_priv, _ = generate_keypair()
    ws = FakeWebSocket(make_signer_responder(remote_priv, remote_pub, result="s3cret"))
    patch_ws(monkeypatch, ws)

    client = BunkerClient(client_priv)
    await client.connect(f"bunker://{remote_pub}?relay={RELAY}&secret=s3cret")
    assert client._remote_pubkey == remote_pub


async def test_connect_error_response_raises(monkeypatch):
    remote_priv, remote_pub = generate_keypair()
    client_priv, _ = generate_keypair()
    ws = FakeWebSocket(make_signer_responder(remote_priv, remote_pub, error="unauthorized"))
    patch_ws(monkeypatch, ws)

    client = BunkerClient(client_priv)
    with pytest.raises(RuntimeError, match="unauthorized"):
        await client.connect(f"bunker://{remote_pub}?relay={RELAY}")


async def test_connect_malformed_netloc_raises(monkeypatch):
    client_priv, _ = generate_keypair()
    patch_ws(monkeypatch, FakeWebSocket())
    client = BunkerClient(client_priv)

    with pytest.raises(ValueError):
        await client.connect(f"bunker://not-a-pubkey?relay={RELAY}")
    with pytest.raises(ValueError):
        await client.connect(f"bunker://npub1invalid?relay={RELAY}")


async def test_connect_timeout_raises(monkeypatch):
    """A non-responsive signer must raise TimeoutError, not hang forever."""
    _, remote_pub = generate_keypair()
    client_priv, _ = generate_keypair()
    ws = FakeWebSocket()  # no responder: never answers
    patch_ws(monkeypatch, ws)

    client = BunkerClient(client_priv)
    with pytest.raises(TimeoutError, match="connect"):
        await client.connect(f"bunker://{remote_pub}?relay={RELAY}", timeout=0.2)
