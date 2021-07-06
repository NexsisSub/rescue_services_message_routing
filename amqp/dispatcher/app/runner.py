import asyncio
import sys
from aio_pika import connect, IncomingMessage, ExchangeType, Message, DeliveryMode, Exchange, Channel
import os 
from functools import partial
from parser import get_recipients_and_protocol_from_edxl_string
import time

ROUTING_EXCHANGE = os.environ.get("ROUTING_EXCHANGE", "routing")
ROUTING_ROUTING_KEY = os.environ.get("ROUTING_ROUTING_KEY", "routing")
ROUTING_QUEUE = os.environ.get("ROUTING_QUEUE", "routing")
DESTINATAIRE = "routing.pompiers-77.cisu"
DISTRIBUTION_QUEUE = os.environ.get("DISTRIBUTION_QUEUE", "distribution")


async def on_message_print(message: IncomingMessage):
    print(f" [->] Route message : {message.routing_key} ")


async def on_message_route_it(channel: Channel, exchange: Exchange, message: IncomingMessage):
    edxl_xml_string = message.body.decode()
    recipients, protocol = get_recipients_and_protocol_from_edxl_string(edxl_xml_string) 

    routing_message = Message(
        message.body,
        delivery_mode=DeliveryMode.PERSISTENT
    )
    for recipient in recipients:
        print(f"Routing to {recipient.address}")
        if recipient.scheme == "sge":
            recipient_queue_name = f"routing.{recipient.address}.{protocol}"
            queue = await channel.declare_queue(recipient_queue_name, durable=True)
            await queue.bind(exchange, routing_key=recipient_queue_name)
            await exchange.publish(routing_message, routing_key=recipient_queue_name)


async def on_message(channel: Channel, exchange: Exchange, message: IncomingMessage):
    await on_message_print(message)
    await on_message_route_it(channel=channel, exchange=exchange, message=message)
    await message.ack()


async def configure_routing_exchange(channel):
    routing_exchange = await channel.declare_exchange(ROUTING_EXCHANGE, ExchangeType.TOPIC)
    return routing_exchange

async def wait_for_rabbitmq_startup(amqp_uri):
    print("wait_for_rabbitmq_startup")
    is_up = False

    while not is_up:
        try:
            connection = await connect(amqp_uri)
            is_up = True
        except Exception as e:
            print(e)
            print("Rabbit Is Not UP")
        time.sleep(5)
        asyncio.sleep(5)
    return True