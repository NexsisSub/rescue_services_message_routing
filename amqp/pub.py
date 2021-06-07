import sys
import asyncio
from aio_pika import connect, Message, DeliveryMode, ExchangeType
import os


ROUTEUR_TOPIC = os.environ.get("ROUTEUR_TOPIC", "routing")
ROUTEUR_EXCHANGE = os.environ.get("ROUTEUR_EXCHANGE", "routing")

AMQP_URI = os.environ.get("AMQP_URI",  "amqp://guest:guest@localhost/")

async def main(loop):
    # Perform connection
    connection = await connect(AMQP_URI, loop=loop)

    # Creating a channel
    channel = await connection.channel()

    topic_logs_exchange = await channel.declare_exchange(
        ROUTEUR_EXCHANGE, ExchangeType.TOPIC
    )

    routing_key = ROUTEUR_TOPIC

    message_body = b"Hello World!"

    message = Message(
        message_body,
        delivery_mode=DeliveryMode.PERSISTENT
    )

    # Sending the message
    await topic_logs_exchange.publish(message, routing_key=routing_key)

    print(" [x] Sent %r" % message)

    await connection.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))