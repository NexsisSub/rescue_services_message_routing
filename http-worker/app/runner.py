import asyncio
import sys
from aio_pika import connect, IncomingMessage, ExchangeType, Message, DeliveryMode, Exchange, Channel
import os 
from functools import partial
from datetime import datetime
import base64
import aiohttp
from parser import SubScriptions


ROUTING_EXCHANGE  = os.environ.get("ROUTING_EXCHANGE")

PROTOCOLS = os.environ.get("PROTOCOLS", "cisu/emsi").split("/")

async def on_message_print(message: IncomingMessage):
    print(f"[->] Received error message dlx data from {message.routing_key}")

async def make_get_requests_and_print_results(uri: str, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(uri, data=data.decode()) as resp:
            print(data.decode())
            print(resp)
            try:
                response = await resp.json()
                print(response)
            except Exception as e:
                print(f"Failed to fetch client {e}")
                

async def on_message_send_it_to_client(subscriptions: SubScriptions, message: IncomingMessage):
    edxl_xml_string = message.body
    receiver = message.headers["receiver"]
    subscription = subscriptions.get_from_sge_name(receiver)
    await make_get_requests_and_print_results(uri=subscription.webhook, data=edxl_xml_string)


async def on_message(subscriptions: SubScriptions, message: IncomingMessage):
    await on_message_print(message)
    try:
        await on_message_send_it_to_client(subscriptions=subscriptions, message=message)
        print("Successfully send message to client")
    except Exception as e:
        print(f"Failed to execute on message because of : {e}")
    finally:
        await message.ack()