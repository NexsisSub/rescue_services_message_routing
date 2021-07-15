import asyncio
import sys
from aio_pika import connect, IncomingMessage, ExchangeType, Message, DeliveryMode, Exchange, Channel
import os 
from functools import partial
from datetime import datetime
import base64
import aiohttp

ROUTING_EXCHANGE  = os.environ.get("ROUTING_EXCHANGE")

PROTOCOLS = os.environ.get("PROTOCOLS", "cisu/emsi").split("/")

async def on_message_print(message: IncomingMessage):
    print(f"[->] Received erro message dlx data from {message.routing_key}")

async def make_get_requests_and_print_results(uri):
    async with aiohttp.ClientSession() as session:
        async with session.get(uri) as resp:
            response = await resp.json()
            print(response["path"])
        

async def on_message_send_it_to_client(subscriptions: dict, message: IncomingMessage):
    edxl_xml_string = message.body.decode()
    receiver = message.headers["receiver"]
    subscription = subscriptions.get(receiver)
    uri = subscription["uri"] if subscription else "http://my-http-listener:8890/not-found"        
    await make_get_requests_and_print_results(uri)


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