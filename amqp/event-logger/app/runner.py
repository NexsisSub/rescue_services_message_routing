import asyncio
import sys
from aio_pika import connect, IncomingMessage, ExchangeType, Message, DeliveryMode, Exchange, Channel
import os 
from functools import partial
from parser import get_recipients_and_protocol_from_edxl_string

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