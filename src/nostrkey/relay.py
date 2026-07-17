"""WebSocket relay client for publishing and subscribing to Nostr events."""

from __future__ import annotations

import asyncio
import ipaddress
import json
import socket
import uuid
from typing import AsyncIterator
from urllib.parse import urlparse

import websockets

from nostrkey.events import NostrEvent


def _is_blocked_address(addr: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    """Return True if an IP address must not be dialed (SSRF guard)."""
    # Unwrap IPv4-mapped IPv6 (e.g. ::ffff:127.0.0.1) so the IPv4 checks apply.
    mapped = getattr(addr, "ipv4_mapped", None)
    if mapped is not None:
        addr = mapped
    return (
        addr.is_loopback
        or addr.is_private
        or addr.is_link_local
        or addr.is_reserved
        or addr.is_multicast
        or addr.is_unspecified
    )


def validate_relay_url(url: str) -> None:
    """Validate a relay URL for scheme and SSRF safety.

    Blocks localhost, private IPs, link-local, multicast, unspecified, and
    reserved addresses to prevent SSRF when relay URLs come from untrusted
    sources (e.g. bunker:// URLs or event content). DNS hostnames are
    resolved via getaddrinfo and EVERY resolved address is checked, so a
    hostname pointing at 169.254.169.254 or 127.0.0.1 is rejected the same
    as a literal IP. Unresolvable hostnames fail closed.

    Note: this validates the addresses at validation time. A hostile DNS
    server that re-resolves differently at connect time (DNS rebinding) is
    only fully defeated by pinning the vetted IP for the actual dial.

    Args:
        url: The relay WebSocket URL to validate.

    Raises:
        ValueError: If the URL is invalid, unresolvable, or points (directly
            or via DNS) to a private/reserved address.
    """
    parsed = urlparse(url)
    if parsed.scheme not in ("ws", "wss"):
        raise ValueError(
            f"Invalid relay URL scheme '{parsed.scheme}': must be ws:// or wss://"
        )

    hostname = parsed.hostname
    if not hostname:
        raise ValueError("Relay URL must include a hostname")

    # Check for localhost aliases
    if hostname in ("localhost", "0.0.0.0"):
        raise ValueError(f"Relay URL must not point to localhost: {hostname}")

    # Literal IP hostname: check it directly.
    try:
        addr = ipaddress.ip_address(hostname)
    except ValueError:
        addr = None

    if addr is not None:
        if _is_blocked_address(addr):
            raise ValueError(
                f"Relay URL must not point to a private or reserved address: {hostname}"
            )
        return

    # DNS hostname: resolve it and apply the same block to every resolved
    # address. A name like metadata.attacker.example -> 169.254.169.254
    # must not bypass the guard.
    port = parsed.port or (443 if parsed.scheme == "wss" else 80)
    try:
        infos = socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ValueError(
            f"Relay URL hostname could not be resolved: {hostname}"
        ) from exc
    if not infos:
        raise ValueError(f"Relay URL hostname could not be resolved: {hostname}")

    for _family, _type, _proto, _canonname, sockaddr in infos:
        try:
            resolved = ipaddress.ip_address(sockaddr[0])
        except ValueError as exc:
            raise ValueError(
                f"Relay URL hostname resolved to an unparseable address: {hostname}"
            ) from exc
        if _is_blocked_address(resolved):
            raise ValueError(
                "Relay URL hostname resolves to a private or reserved address: "
                f"{hostname} -> {resolved}"
            )


class RelayClient:
    """Async WebSocket client for a Nostr relay.

    Usage:
        async with RelayClient("wss://relay.nostrkeep.com") as relay:
            await relay.publish(event)

            async for event in relay.subscribe([{"kinds": [1], "limit": 10}]):
                print(event)
    """

    def __init__(self, url: str):
        validate_relay_url(url)
        self.url = url
        self._ws = None

    async def __aenter__(self):
        self._ws = await websockets.connect(self.url, open_timeout=30)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._ws:
            await self._ws.close()

    async def publish(self, event: NostrEvent) -> bool:
        """Publish a signed event to the relay.

        Returns True if the relay accepted the event.
        """
        if not self._ws:
            raise RuntimeError("Not connected — use 'async with RelayClient(url) as relay:'")

        msg = json.dumps(["EVENT", event.to_dict()])
        await self._ws.send(msg)

        response = await asyncio.wait_for(self._ws.recv(), timeout=30)
        data = json.loads(response)
        if data[0] == "OK" and data[2] is True:
            return True
        return False

    async def subscribe(
        self, filters: list[dict], subscription_id: str | None = None
    ) -> AsyncIterator[NostrEvent]:
        """Subscribe to events matching the given filters.

        Args:
            filters: List of filter objects per NIP-01.
            subscription_id: Optional subscription ID (auto-generated if not provided).

        Yields:
            NostrEvent objects matching the filters.
        """
        if not self._ws:
            raise RuntimeError("Not connected — use 'async with RelayClient(url) as relay:'")

        sub_id = subscription_id or str(uuid.uuid4())
        msg = json.dumps(["REQ", sub_id, *filters])
        await self._ws.send(msg)

        async for raw in self._ws:
            data = json.loads(raw)
            if data[0] == "EVENT" and data[1] == sub_id:
                evt = data[2]
                yield NostrEvent(
                    id=evt["id"],
                    pubkey=evt["pubkey"],
                    created_at=evt["created_at"],
                    kind=evt["kind"],
                    tags=evt["tags"],
                    content=evt["content"],
                    sig=evt["sig"],
                )
            elif data[0] == "EOSE" and data[1] == sub_id:
                break

    async def close_subscription(self, subscription_id: str) -> None:
        """Close a subscription."""
        if self._ws:
            await self._ws.send(json.dumps(["CLOSE", subscription_id]))
