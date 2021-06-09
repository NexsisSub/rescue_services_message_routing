import asyncio
import sys
from aio_pika import connect, IncomingMessage, ExchangeType, Message, DeliveryMode, Exchange
import os 
from functools import partial

ROUTING_EXCHANGE = os.environ.get("ROUTING_EXCHANGE", "routing")
ROUTING_ROUTING_KEY = os.environ.get("ROUTING_ROUTING_KEY", "routing")
ROUTING_QUEUE = os.environ.get("ROUTING_QUEUE", "routing")
DESTINATAIRE = "routing.pompiers-77.cisu"
MAIN_QUEUE = os.environ.get("MAIN_QUEUE", "main")

AMQP_URI = os.environ.get("AMQP_URI",  "amqp://guest:guest@localhost/")

DESTINATAIRES = ["pompiers-77", "samu-77"]
PROTOCOLS = ["cisu", "emsi"]


async def on_message_print(message: IncomingMessage):
    print(" [x] %r:%r" % (message.routing_key, message.body))


async def on_message_route_it(exchange: Exchange, message: IncomingMessage):    
    routing_message = Message(
        message.body,
        delivery_mode=DeliveryMode.PERSISTENT
    )
    await exchange.publish(
        routing_message,
        routing_key="routing.pompiers-77.cisu"
    )


async def on_message(exchange: Exchange, message: IncomingMessage):
    await on_message_print(message)
    await on_message_route_it(exchange=exchange, message=message)
    await message.ack()


async def configure_routing_exchange(channel):
    routing_exchange = await channel.declare_exchange(ROUTING_EXCHANGE, ExchangeType.DIRECT)
    for destinataire in DESTINATAIRES:
        for protocol in PROTOCOLS:
            queue = await channel.declare_queue(f"routing.{destinataire}.{protocol}", durable=True)
            await queue.bind(routing_exchange, routing_key=f"routing.{destinataire}.{protocol}")
    return routing_exchange


async def main(loop):
    # Perform connection
    connection = await connect(AMQP_URI, loop=loop)

    # Creating a channel
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)

    # Declare an exchange

    queue = await channel.declare_queue(MAIN_QUEUE, durable=True)

    routing_exchange = await configure_routing_exchange(channel)

    await queue.consume(partial(on_message, routing_exchange))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main(loop))

    # we enter a never-ending loop that waits for
    # data and runs callbacks whenever necessary.
    print(" [*] Waiting for messages. To exit press CTRL+C")
    loop.run_forever()