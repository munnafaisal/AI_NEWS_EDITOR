#!/usr/bin/env python

"""Client using the asyncio API."""

import asyncio
from websockets.asyncio.client import connect
import json

#event = {'action': "scrap", "name": "new age", "date": "2024-08-05"}
event = {'action': "scrap", "name": "new age", "date": "test", "QS": "what about army chief?"}
#event = {'action': "close", "name": "new age", "date": "test", "QS": "who are you?"}
async def hello(my_event):
    async with connect("ws://localhost:8765") as websocket:
        await websocket.send(json.dumps(my_event))
        while True:
            message = await websocket.recv()
            print(message)
            if message == "close":
                #print(message)
                websocket.close()
                break


if __name__ == "__main__":

    event["QS"] = "what about army chief's statement?"
    asyncio.run(hello(my_event=event))

