#!/usr/bin/env python

"""Echo server using the asyncio API."""

import asyncio
import time
import json
from websockets.asyncio.server import serve


async def echo(websocket):
    async for message in websocket:
        message = json.loads(message)['action']
        if message == "close":
            break
        await websocket.send(message)
        #await websocket.send("close")


async def main():
    async with serve(echo, "localhost", 8765) as server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())