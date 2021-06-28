import asyncio
import sys
from aio_pika import connect, IncomingMessage, ExchangeType, Message, DeliveryMode, Exchange
import os 
from functools import partial
from parser import parse_xml_string_to_dict
from elasticsearch import Elasticsearch


EVENT_LOGGER_QUEUE = os.environ.get("EVENT_LOGGER_QUEUE", "event_logger")



async def main(loop):
    # Perform connection
    connection = await connect(AMQP_URI, loop=loop)

    # Creating a channel
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)

    # Declare an exchange
    queue = await channel.declare_queue(EVENT_LOGGER_QUEUE, durable=True)
    es_client = Elasticsearch(ELASTIC_URI, timeout=60)


    await queue.consume(partial(on_message, es_client))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main(loop))

    # we enter a never-ending loop that waits for
    # data and runs callbacks whenever necessary.
    print(" [*] Waiting for messages. To exit press CTRL+C")
    loop.run_forever()