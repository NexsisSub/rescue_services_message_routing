import sys
import asyncio
from aio_pika import connect, Message, DeliveryMode, ExchangeType
import os

MAIN_EXCHANGE = os.environ.get("MAIN_EXCHANGE", "distribution")
MAIN_ROUTING_KEY = os.environ.get("MAIN_ROUTING_KEY", "distribution")

AMQP_URI = os.environ.get("AMQP_URI",  "amqp://guest:guest@192.168.0.147:5672/")

async def main(loop):
    # Perform connection
    connection = await connect(AMQP_URI, loop=loop)

    # Creating a channel
    channel = await connection.channel()

    main_exchange = await channel.declare_exchange(
        MAIN_EXCHANGE, ExchangeType.DIRECT
    )

    with open("./data/9a009967-00f6-480c-aa70-78ffe52221fc.xml", 'rb') as f : 
        cisu_message = f.read()
    
    message = Message(
        cisu_message,
        delivery_mode=DeliveryMode.PERSISTENT
    )

    # Sending the message
    await main_exchange.publish(message, routing_key=MAIN_ROUTING_KEY)

    print(" [x] Sent %r" % message)

    await connection.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))