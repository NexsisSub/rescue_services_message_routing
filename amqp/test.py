import asyncio
import sys
from aio_pika import connect, IncomingMessage, ExchangeType, Message, DeliveryMode, Exchange
import os 
from functools import partial
from dotenv import load_dotenv

DISTRIBUTION_EXCHANGE = os.environ.get("MAIN_EXCHANGE", "distribution")
DISTRIBUTION_ROUTING_KEY = os.environ.get("DISTRIBUTION_ROUTING_KEY", "distribution")
DISTRIBUTION_QUEUE = os.environ.get("DISTRIBUTION_QUEUE", "distribution")
ROUTING_EXCHANGE = os.environ.get("ROUTING_EXCHANGE", "routing")

EVENT_LOGGER_QUEUE = os.environ.get("EVENT_LOGGER_QUEUE", "event_logger")
AMQP_URI = os.environ.get("AMQP_URI",  "amqp://guest:guest@localhost:5672/")

async def configure_distribution_exchange(channel):
    distribution_exchange = await channel.declare_exchange(DISTRIBUTION_EXCHANGE, ExchangeType.TOPIC)

    distribution_queue = await channel.declare_queue(DISTRIBUTION_QUEUE, durable=True)
    await distribution_queue.bind(distribution_exchange, routing_key=DISTRIBUTION_ROUTING_KEY)
    return distribution_exchange

async def configure_routing_exchange(channel):
    routing_exchange = await channel.declare_exchange(ROUTING_EXCHANGE, ExchangeType.TOPIC)
    event_logger_queue = await channel.declare_queue(EVENT_LOGGER_QUEUE, durable=True)
    await event_logger_queue.bind(routing_exchange, routing_key="routing.#")
    return routing_exchange


async def main(loop):
    # Perform connection
    connection = await connect(AMQP_URI, loop=loop)

    # Creating a channel
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)

    # Declare an exchange
    main_exchange = await configure_distribution_exchange(channel)
    main_exchange = await configure_routing_exchange(channel)



if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
