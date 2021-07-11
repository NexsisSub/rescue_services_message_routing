import asyncio
import sys
from aio_pika import connect, IncomingMessage, ExchangeType, Message, DeliveryMode, Exchange, Channel
import os 
from functools import partial
from datetime import datetime


async def on_message_print(message: IncomingMessage):
    print(f"[->] Received erro message dlx data from {message.routing_key}")

async def on_message(message: IncomingMessage):
    await on_message_print(message)
    await message.ack()

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