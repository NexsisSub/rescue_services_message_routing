import sys
import asyncio
from aio_pika import connect, Message, DeliveryMode, ExchangeType
import os

MAIN_TOPIC = os.environ.get("ROUTEUR_TOPIC", "main")
MAIN_EXCHANGE = os.environ.get("ROUTEUR_EXCHANGE", "main")


AMQP_URI = os.environ.get("AMQP_URI",  "amqp://guest:guest@localhost/")

async def main(loop):
    # Perform connection
    connection = await connect(AMQP_URI, loop=loop)

    # Creating a channel
    channel = await connection.channel()

    main_exchange = await channel.declare_exchange(
        MAIN_EXCHANGE, ExchangeType.TOPIC
    )
    
    message_body = b"Hello World!"

    message = Message(
        message_body,
        delivery_mode=DeliveryMode.PERSISTENT
    )

    # Sending the message
    await main_exchange.publish(message, routing_key=MAIN_TOPIC)

    print(" [x] Sent %r" % message)

    await connection.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))