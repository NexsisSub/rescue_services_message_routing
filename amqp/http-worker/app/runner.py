import asyncio
import sys
from aio_pika import connect, IncomingMessage, ExchangeType, Message, DeliveryMode, Exchange, Channel
import os 
from functools import partial
from datetime import datetime
from parser import get_sender_and_protocol_from_edxl_string, Sender
import base64
import requests


content = 'This is about page'
env = Environment(loader=FileSystemLoader('templates'))

ROUTING_EXCHANGE  = os.environ.get("ROUTING_EXCHANGE")

PROTOCOLS = os.environ.get("PROTOCOLS", "cisu/emsi").split("/")

async def on_message_print(message: IncomingMessage):
    print(f"[->] Received erro message dlx data from {message.routing_key}")

async def on_message_send_it_to_client(subscriptions: dict, message: IncomingMessage):
    edxl_xml_string = message.body.decode()
    recipients, protocol = get_recipients_and_protocol_from_edxl_string(edxl_xml_string) 

    subscription = subscriptions.get(recipients[0].address)
    if subscription: 
        uri = subscription["uri"]
        response = requests.get(uri)
        print(response.json())

async def on_message(subscriptions: dict, message: IncomingMessage):
    await on_message_print(message)
    try:
        await on_message_send_it_to_client(subscriptions=subscriptions, message=message)
    except Exception as e:
        print(e)
    finally:
        await message.ack()


async def configure_routing_exchange(channel):
    routing_exchange = await channel.declare_exchange(ROUTING_EXCHANGE, ExchangeType.TOPIC)

    for protocol in PROTOCOLS:
        all_routing_queue = await channel.declare_queue(f"routing.all.{protocol}", durable=True)
        await all_routing_queue.bind(routing_exchange, routing_key=f"#.{protocol}")

    return routing_exchange


async def wait_for_rabbitmq_startup(amqp_uri):
    print("wait_for_rabbitmq_startup")
    http_uri = amqp_uri.replace("5672/", "15672/api/aliveness-test/%2F").replace("amqp", "http")
    is_up = False

    while not is_up:
        try:
            connection = await connect(amqp_uri)
            is_up = True
        except Exception as e:
            print(e)
        asyncio.sleep(5)
    return True