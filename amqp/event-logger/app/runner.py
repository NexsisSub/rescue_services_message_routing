import asyncio
import sys
from aio_pika import connect, IncomingMessage, ExchangeType, Message, DeliveryMode, Exchange, Channel
import os 
from functools import partial
from parser import parse_xml_string_to_dict, get_protocol_from_xml_string
from elasticsearch import Elasticsearch
from datetime import datetime


AMQP_URI = os.environ.get("AMQP_URI",  "amqp://guest:guest@localhost/")
ELASTIC_URI = os.environ.get("ELASTIC_URI",  "0.0.0.0:9200")

async def on_message_log_it(es_client: Elasticsearch, message: IncomingMessage):
    xml_string = message.body.decode()
    protocol = get_protocol_from_xml_string(xml_string)
    edxl_data = parse_xml_string_to_dict(message.body.decode())
    print(f"logging on routing-{protocol}-{datetime.today().strftime('%Y-%m-%d')}")
    res = es_client.index(
        index=f"routing-{protocol}-{datetime.today().strftime('%Y-%m-%d')}", 
        id=edxl_data["edxlDistribution"]["distributionID"], 
        body=edxl_data
    )

async def on_message_print(message: IncomingMessage):
    print(f"[->] Store data from {message.routing_key}")

async def on_message(es_client: Elasticsearch, message: IncomingMessage):
    await on_message_print(message)
    await on_message_log_it(es_client=es_client, message=message)
    await message.ack()