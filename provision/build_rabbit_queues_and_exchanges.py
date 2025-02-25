import asyncio
import sys
from aio_pika import connect, IncomingMessage, ExchangeType, Message, DeliveryMode, Exchange
import os 
from functools import partial

DISTRIBUTION_EXCHANGE = os.environ.get("MAIN_EXCHANGE", "distribution")
DISTRIBUTION_ROUTING_KEY = os.environ.get("DISTRIBUTION_ROUTING_KEY", "distribution")
DISTRIBUTION_QUEUE = os.environ.get("DISTRIBUTION_QUEUE", "distribution")

ROUTING_EXCHANGE = os.environ.get("ROUTING_EXCHANGE", "routing")

DLX_QUEUE = os.environ.get("DLX_QUEUE", "dlx_queue")
DLX_EXCHANGE = os.environ.get("DLX_EXCHANGE", "dlx")

EVENT_LOGGER_QUEUE = os.environ.get("EVENT_LOGGER_QUEUE", "event_logger")
AMQP_URI = os.environ.get("AMQP_URI",  "amqp://guest:guest@localhost:5672/")

PROTOCOLS = os.environ.get("PROTOCOLS", "cisu/emsi").split("/")


print(AMQP_URI)
async def configure_distribution_exchange(channel):
    distribution_exchange = await channel.declare_exchange(DISTRIBUTION_EXCHANGE, ExchangeType.TOPIC)

    distribution_queue = await channel.declare_queue(DISTRIBUTION_QUEUE, durable=True)
    await distribution_queue.bind(distribution_exchange, routing_key=DISTRIBUTION_ROUTING_KEY,   
    arguments={
        "x-dead-letter-exchange" : "dlx",
        }
    )
    return distribution_exchange

async def configure_routing_exchange(channel):
    routing_exchange = await channel.declare_exchange(ROUTING_EXCHANGE, ExchangeType.TOPIC)
    event_logger_queue = await channel.declare_queue(EVENT_LOGGER_QUEUE, durable=True)
    await event_logger_queue.bind(routing_exchange, routing_key="routing.#")
    return routing_exchange

async def configure_dead_letter_exchange(channel):
    dead_letter_exchange = await channel.declare_exchange(DLX_EXCHANGE, ExchangeType.TOPIC)

    for protocol in PROTOCOLS:
        dead_letter_queue = await channel.declare_queue(f"{DLX_QUEUE}.{protocol}", durable=True)
        await dead_letter_queue.bind(dead_letter_exchange, routing_key=f"#.{protocol}")

    return dead_letter_exchange

async def main(loop):
    # Perform connection
    connection = await connect(AMQP_URI, loop=loop)

    # Creating a channel
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)

    # Declare an exchange
    main_exchange = await configure_distribution_exchange(channel=channel)
    routing_exchange = await configure_routing_exchange(channel=channel)
    dlx = await configure_dead_letter_exchange(channel=channel)



if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
