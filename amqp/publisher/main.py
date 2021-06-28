import sys
import asyncio
from aio_pika import connect, Message, DeliveryMode, ExchangeType
import os
import logging
DISTRIBUTION_EXCHANGE = os.environ.get("DISTRIBUTION_EXCHANGE", "distribution")
DISTRIBUTION_ROUTING_KEY = os.environ.get("DISTRIBUTION_ROUTING_KEY", "distribution")

AMQP_URI = os.environ.get("AMQP_URI",  "amqp://guest:guest@localhost:5672/")

async def main(loop):
    # Perform connection
    connection = await connect(AMQP_URI, loop=loop)

    # Creating a channel
    channel = await connection.channel()

    main_exchange = await channel.declare_exchange(
        DISTRIBUTION_EXCHANGE, ExchangeType.TOPIC
    )

    with open("./data/9a009967-00f6-480c-aa70-78ffe52221fc.xml", 'rb') as f : 
        cisu_message = f.read()

    logging.info(f"[->] Send message to {DISTRIBUTION_ROUTING_KEY}")
    
    
    message = Message(
        cisu_message,
        delivery_mode=DeliveryMode.PERSISTENT
    )

    # Sending the message
    await main_exchange.publish(message, routing_key=DISTRIBUTION_ROUTING_KEY)

    print(" [x] Sent %r" % message)

    await connection.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))