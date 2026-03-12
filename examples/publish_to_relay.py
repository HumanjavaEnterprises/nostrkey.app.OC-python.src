"""Example — create an identity and publish an event to a relay."""

import asyncio

from nostrkey import Identity
from nostrkey.relay import RelayClient


async def main():
    # Create or load your bot identity
    bot = Identity.generate()
    print(f"Bot npub: {bot.npub}")

    # Sign an event
    event = bot.sign_event(
        kind=1,
        content="Live from an OpenClaw bot!",
        tags=[["t", "openclaw"]],
    )

    # Publish to a relay
    async with RelayClient("wss://relay.damus.io") as relay:
        accepted = await relay.publish(event)
        if accepted:
            print(f"Event published: {event.id}")
        else:
            print("Event rejected by relay")


if __name__ == "__main__":
    asyncio.run(main())
