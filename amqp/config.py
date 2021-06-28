import asyncio
import sys
from aio_pika import connect, IncomingMessage, ExchangeType, Message, DeliveryMode, Exchange
import os 
from functools import partial

MAIN_EXCHANGE = os.environ.get("MAIN_EXCHANGE", "distribution")
MAIN_ROUTING_KEY = os.environ.get("MAIN_ROUTING_KEY", "distribution")
MAIN_QUEUE = os.environ.get("MAIN_QUEUE", "distribution")
EVENT_LOGGER_QUEUE = os.environ.get("EVENT_LOGGER_QUEUE", "event_logger")
AMQP_URI = os.environ.get("AMQP_URI",  "amqp://guest:guest@192.168.0.147:5672/")


async def configure_main_exchange(channel):
    main_exchange = await channel.declare_exchange(MAIN_EXCHANGE, ExchangeType.DIRECT)

    main_queue = await channel.declare_queue(MAIN_QUEUE, durable=True)
    await main_queue.bind(main_exchange, routing_key=MAIN_ROUTING_KEY)

    event_logger_queue = await channel.declare_queue(EVENT_LOGGER_QUEUE, durable=True)
    await event_logger_queue.bind(main_exchange, routing_key=MAIN_ROUTING_KEY)
    return main_exchange


async def main(loop):
    # Perform connection
    connection = await connect(AMQP_URI, loop=loop)

    # Creating a channel
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)

    # Declare an exchange
    main_exchange = await configure_main_exchange(channel)



if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
