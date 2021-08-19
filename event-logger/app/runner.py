import asyncio
import sys
from aio_pika import connect, IncomingMessage, ExchangeType, Message, DeliveryMode, Exchange, Channel
import os 
from functools import partial
from parser import parse_xml_string_to_dict
from elasticsearch import Elasticsearch
from datetime import datetime
import requests

AMQP_URI = os.environ.get("AMQP_URI",  "amqp://guest:guest@localhost:5672/")
ELASTIC_URI = os.environ.get("ELASTIC_URI",  "0.0.0.0:9200")


async def clean_xml_data(edxl_data):
    pass

async def on_message_log_it(es_client: Elasticsearch, message: IncomingMessage):
    xml_string = message.body.decode()
    protocol: str = message.headers["protocol"]
    edxl_data = parse_xml_string_to_dict(message.body.decode())
    res = es_client.index(
        index=f"routing-{protocol}-{datetime.today().strftime('%Y-%m-%d')}", 
        id=edxl_data["edxlDistribution"]["distributionID"], 
        body=edxl_data
    )

async def on_message_print(message: IncomingMessage):
    print(f"[->] Store data from {message.routing_key}")

async def on_message(es_client: Elasticsearch, message: IncomingMessage):
    try:
        await on_message_print(message)
        await on_message_log_it(es_client=es_client, message=message)
        print("Successfully store data on Elastic")
    except Exception as e:
        print(f"Failed to store data on Elastic because of {e}")
    finally:
        await message.ack()
