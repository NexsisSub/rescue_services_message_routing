

import argparse, sys
import asyncio
import os
import signal
from nats.aio.client import Client as NATS
import json
import elasticsearch 

NATS_URI = os.environ.get("NATS_URI",  "nats://127.0.0.1:4222")
EVENT_DATA_SUBJECT = os.environ.get("EVENT_DATA_SUBJECT", "event_data")

async def run(loop):
    nc = NATS()

    async def error_cb(e):
        print("Error:", e)

    async def closed_cb():
        print("Connection to NATS is closed.")
        await asyncio.sleep(0.1, loop=loop)
        loop.stop()

    async def reconnected_cb():
        print(f"Connected to NATS at {nc.connected_url.netloc}...")

    async def subscribe_handler(msg):
        subject = msg.subject
        reply = msg.reply
        data = json.loads(msg.data.decode())
        print("Received a message on '{subject} {reply}': {data}".format(
          subject=subject, reply=reply, data=data))

        res = es.index(index="test-index", id=1, body=doc)
    options = {
        "servers":[NATS_URI],
        "loop": loop,
        "error_cb": error_cb,
        "closed_cb": closed_cb,
        "reconnected_cb": reconnected_cb
    }

    await nc.connect(**options)

    print(f"Connected to NATS at {nc.connected_url.netloc}...")

    await nc.subscribe(EVENT_DATA_SUBJECT, "", subscribe_handler)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    try:
        loop.run_forever()
    finally:
        loop.close()
