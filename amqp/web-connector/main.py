import asyncio
import sys
from aio_pika import connect, IncomingMessage, ExchangeType, Message, DeliveryMode, Exchange
import os 
from functools import partial


AMQP_URI = os.environ.get("AMQP_URI",  "amqp://guest:guest@localhost/")

DESTINATAIRE = "pompiers-77"
PROTOCOL = "cisu"


async def on_message_print(message: IncomingMessage):
    print(" [x] %r:%r" % (message.routing_key, message.body))


async def on_message(message: IncomingMessage):
    await on_message_print(message)
    message.ack()


async def main(loop):
    # Perform connection
    connection = await connect(AMQP_URI, loop=loop)

    # Creating a channel
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)

    # Declare an exchange

    queue = await channel.declare_queue(f"routing.{DESTINATAIRE}.{PROTOCOL}", durable=True)

    await queue.consume(on_message)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main(loop))

    # we enter a never-ending loop that waits for
    # data and runs callbacks whenever necessary.
    print(" [*] Waiting for messages. To exit press CTRL+C")
    loop.run_forever()