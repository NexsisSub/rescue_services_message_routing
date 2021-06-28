import asyncio
import sys
from aio_pika import connect, IncomingMessage, ExchangeType, Message, DeliveryMode, Exchange
import os 
from functools import partial
from parser import parse_xml_string_to_dict
from elasticsearch import Elasticsearch


EVENT_LOGGER_QUEUE = os.environ.get("EVENT_LOGGER_QUEUE", "event_logger")

AMQP_URI = os.environ.get("AMQP_URI",  "amqp://guest:guest@localhost/")
ELASTIC_URI = os.environ.get("ELASTIC_URI",  "0.0.0.0:9200")

async def on_message_log_it(es_client: Elasticsearch, message: IncomingMessage):
    edxl_data = parse_xml_string_to_dict(message.body.decode())
    res = es_client.index(index="test-index", id=edxl_data["edxlDistribution"]["distributionID"], body=edxl_data)

async def on_message_print(message: IncomingMessage):
    print(f"[->] Store data from {message.routing_key}")

async def on_message(es_client: Elasticsearch, message: IncomingMessage):
    await on_message_print(message)
    await on_message_log_it(es_client=es_client, message=message)
    await message.ack()


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