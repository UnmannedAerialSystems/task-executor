import asyncio


async def delayed_trigger(delay: int = 5):
    for i in range(delay, 0, -1):
        if i % 5 == 0 or i <= 5:
            print(f"Triggering immediate task in {i} seconds...")
        await asyncio.sleep(1)
    return