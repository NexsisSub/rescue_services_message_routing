import asyncio
import sys
from aio_pika import connect, IncomingMessage, ExchangeType, Message, DeliveryMode, Exchange, Channel
import os 
from functools import partial
from datetime import datetime
from parser import get_sender_and_protocol_from_edxl_string, Sender


ERRORS_EXCHANGE  = os.environ.get("ERRORS_EXCHANGE")


async def on_message_print(message: IncomingMessage):
    print(f"[->] Received erro message dlx data from {message.routing_key}")

async def on_message_route_it_to_client_error_queue(channel: Channel, exchange: Exchange, message: IncomingMessage):
    edxl_xml_string = message.body.decode()
    sender: Sender = get_sender_and_protocol_from_edxl_string(edxl_xml_string)
    error_message = Message(
        f"error from queue {message.routing_key}".encode(),
        delivery_mode=DeliveryMode.PERSISTENT,
        expiration=None
    )
    recipient_queue_name = f"errors.{sender.name}.messaging"
    queue = await channel.declare_queue(recipient_queue_name, durable=True)
    await queue.bind(exchange, routing_key=recipient_queue_name)
    await exchange.publish(error_message, routing_key=recipient_queue_name)

async def on_message(channel: Channel, exchange: Exchange, message: IncomingMessage):
    await on_message_print(message)
    await on_message_route_it_to_client_error_queue(channel=channel, exchange=exchange, message=message)
    await message.ack()


async def configure_errors_exchange(channel):
    errors_exchange = await channel.declare_exchange(ERRORS_EXCHANGE, ExchangeType.TOPIC)
    return errors_exchange


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