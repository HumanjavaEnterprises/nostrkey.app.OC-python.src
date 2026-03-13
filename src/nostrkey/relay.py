"""WebSocket relay client for publishing and subscribing to Nostr events."""

from __future__ import annotations

import asyncio
import json
import uuid
from typing import AsyncIterator
from urllib.parse import urlparse

import websockets

from nostrkey.events import NostrEvent


class RelayClient:
    """Async WebSocket client for a Nostr relay.

    Usage:
        async with RelayClient("wss://relay.nostrkeep.com") as relay:
            await relay.publish(event)

            async for event in relay.subscribe([{"kinds": [1], "limit": 10}]):
                print(event)
    """

    def __init__(self, url: str):
        parsed = urlparse(url)
        if parsed.scheme not in ("ws", "wss"):
            raise ValueError(
                f"Invalid relay URL scheme '{parsed.scheme}': must be ws:// or wss://"
            )
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
