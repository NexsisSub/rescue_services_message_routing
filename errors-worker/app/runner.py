import asyncio
import sys
from aio_pika import connect, IncomingMessage, ExchangeType, Message, DeliveryMode, Exchange, Channel
import os 
from functools import partial
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import base64
import json
from uuid import uuid4


env = Environment(loader=FileSystemLoader('templates'))

ERRORS_EXCHANGE  = os.environ.get("ERRORS_EXCHANGE")


async def on_message_print(message: IncomingMessage):
    print(f"[->] Received error message dlx data from queue : {message.routing_key}")

async def on_message_route_it_to_client_error_queue(channel: Channel, exchange: Exchange, message: IncomingMessage):
    edxl_xml_string = message.body.decode()
    
    sender: str = message.headers["sender"]
    receiver: str = message.headers["receiver"]
    messageID: str = message.headers["messageID"]

    message_content = json.dumps({
        #"message_data":message.body.decode(),
        "cause":{"code":"CONFLIT"},
        "idCorrelationMessage":messageID
        }).encode()

    distribution_id = str(uuid4())

    message_content = build_error_message(
        sender_id=receiver,
        receiver_id=sender,
        distribution_id=distribution_id,
        content=base64.b64encode(message_content).decode()
    )

    error_message = Message(
        message_content.encode(),
        delivery_mode=DeliveryMode.PERSISTENT,
        expiration=None,
        headers={
                "distribution_id":distribution_id,
                "receiver":sender,
                "sender": receiver,
            }
    )

    recipient_queue_name = f"messaging.{sender}.errors"
    queue = await channel.declare_queue(recipient_queue_name, durable=True)
    await queue.bind(exchange, routing_key=recipient_queue_name)
    await exchange.publish(error_message, routing_key=recipient_queue_name)
    print(f"Succesfully route data to {recipient_queue_name} ")


async def on_message(channel: Channel, exchange: Exchange, message: IncomingMessage):
    try:
        await on_message_print(message)
        await on_message_route_it_to_client_error_queue(channel=channel, exchange=exchange, message=message)
        print("Successfully route message")
    except Exception as e:
        print(f"Failed to route error message beacause of : {e}")
    finally:
        await message.ack()
        print("Succesffully Acked message")

def build_error_message(sender_id: str, receiver_id: str, content: str, distribution_id: str):
    template = env.get_template('error.xml')
    output = template.render(
        sender_id=sender_id, 
        receiver_id=receiver_id,
        distributionID=distribution_id,
        content=content)
        
    return output


async def configure_errors_exchange(channel):
    errors_exchange = await channel.declare_exchange(ERRORS_EXCHANGE, ExchangeType.TOPIC)
    return errors_exchange