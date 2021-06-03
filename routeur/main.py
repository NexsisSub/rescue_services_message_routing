

import argparse, sys
import asyncio
import os
import signal
from nats.aio.client import Client as NATS
import json


async def run(loop):
    ROUTEUR_SUBJECT = os.environ.get("ROUTEUR_SUBJECT", "routing")
    EVENT_DATA_SUBJECT = os.environ.get("EVENT_DATA_SUBJECT", "event_data")
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
        for destinataire in data["destinataires"]:
            await nc.publish(f"routing.{destinataire}", "contact this force".encode())

    async def publish_event_data(msg):
        data = msg.data
        print("Received a message on {data}".format(data=data))
        await nc.publish(EVENT_DATA_SUBJECT, data)

    options = {
        "servers":["nats://nats:4222"],
        "loop": loop,
        "error_cb": error_cb,
        "closed_cb": closed_cb,
        "reconnected_cb": reconnected_cb
    }

    await nc.connect(**options)

    print(f"Connected to NATS at {nc.connected_url.netloc}...")
    # def signal_handler():
    #     if nc.is_closed:
    #         return
    #     print("Disconnecting...")
    #     loop.create_task(nc.close())

    # for sig in ('SIGINT', 'SIGTERM'):
    #     loop.add_signal_handler(getattr(signal, sig), signal_handler)

    await nc.subscribe(ROUTEUR_SUBJECT, "", subscribe_handler)
    await nc.subscribe(ROUTEUR_SUBJECT, "", publish_event_data)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    try:
        loop.run_forever()
    finally:
        loop.close()