import asyncio
import sys
from aio_pika import connect, IncomingMessage, ExchangeType, Message, DeliveryMode, Exchange, Channel
import os 
from functools import partial
from parser import get_recipients_and_protocol_from_edxl_string, get_distribution_and_message_id
import time
from services import create_event
from  schema import Event as EventSchema
from datetime import datetime
from elasticsearch import Elasticsearch


ROUTING_EXCHANGE = os.environ.get("ROUTING_EXCHANGE", "routing")
ROUTING_ROUTING_KEY = os.environ.get("ROUTING_ROUTING_KEY", "routing")
ROUTING_QUEUE = os.environ.get("ROUTING_QUEUE", "routing")
DESTINATAIRE = "routing.pompiers-77.cisu"
DISTRIBUTION_QUEUE = os.environ.get("DISTRIBUTION_QUEUE", "distribution")


async def on_message_print(message: IncomingMessage):
    print(f" [->] Route message : {message.routing_key} ")

async def on_message_route_it(channel: Channel, exchange: Exchange, message: IncomingMessage):
    edxl_xml_string = message.body.decode()
    recipients, sender, protocol = get_recipients_and_protocol_from_edxl_string(edxl_xml_string) 
    distributionID, messageID = get_distribution_and_message_id(edxl_xml_string)

    for recipient in recipients:
        routing_message = Message(
            message.body,
            delivery_mode=DeliveryMode.PERSISTENT,
            expiration=message.headers.get("ttl"),
            headers={
                "receiver":recipient.address,
                "sender": sender.name,
                "recipients": [recipient.address for recipient in recipients],
                "protocol": protocol,
                "distributionID": distributionID,
                "messageID": messageID
            }
        )
        print(f"Routing to {recipient.scheme}.{recipient.address}")
        if recipient.scheme == "sge":
            recipient_queue_name = f"routing.{recipient.address}.{protocol}"
            queue = await channel.declare_queue(recipient_queue_name, durable=True, arguments={
                "x-dead-letter-exchange" : "dlx",
            })
            await queue.bind(exchange, routing_key=recipient_queue_name)
            await exchange.publish(routing_message, routing_key=recipient_queue_name)
            print(f"Successfully publish message to {recipient_queue_name}")

async def on_message(channel: Channel, exchange: Exchange, elastic_client: Elasticsearch, message: IncomingMessage,):
    routed_at = datetime.now()
    await on_message_print(message)
    try:
        await on_message_route_it(channel=channel, exchange=exchange, message=message)
        create_event(elastic_client=elastic_client, event=EventSchema(raw=message.body.decode(), status="success", routed_at=routed_at))
    except Exception as e:
        print(f"Failed to execute on message because of {e}")
        create_event(elastic_client=elastic_client, event=EventSchema(raw=message.body.decode(), status="failed", routed_at=routed_at, reason=str(e)))
    finally:
        await message.ack()
    


async def configure_routing_exchange(channel):
    routing_exchange = await channel.declare_exchange(ROUTING_EXCHANGE, ExchangeType.TOPIC)
    return routing_exchange