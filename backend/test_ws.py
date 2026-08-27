import asyncio
import websockets


async def test():

    async with websockets.connect(
        "ws://127.0.0.1:8000/chat"
    ) as ws:

        await ws.send("legal risk")

        response = await ws.recv()

        print(response)


if __name__ == "__main__":
    asyncio.run(test())