import asyncio
import sys
from aio_pika import connect, IncomingMessage, ExchangeType, Message, DeliveryMode
import os 


MAIN_TOPIC = os.environ.get("ROUTEUR_TOPIC", "main")
MAIN_EXCHANGE = os.environ.get("ROUTEUR_EXCHANGE", "main")

ROUTING_EXCHANGE = os.environ.get("ROUTING_EXCHANGE", "routing")
ROUTING_TOPIC = os.environ.get("ROUTING_TOPIC", "routing")

EVENT_DATA_EXCHANGE = os.environ.get("ROUTING_EXCHANGE", "event_data")
EVENT_DATA_TOPIC = os.environ.get("ROUTING_TOPIC", "event_data")

AMQP_URI = os.environ.get("AMQP_URI",  "amqp://guest:guest@localhost/")

async def on_message_print(message: IncomingMessage):
    with message.process():
        print(" [x] %r:%r" % (message.routing_key, message.body))

async def on_message_route_it(message: IncomingMessage, routing_exchange):
    routing_message = Message(
        message.body,
        delivery_mode=DeliveryMode.PERSISTENT
    )
    await routing_exchange.publish(
        routing_message,
        routing_key="routing.pompiers-77.cisu"
    )

async def on_message_log_it(message: IncomingMessage, event_logger_exchange):
    routing_message = Message(
        message.body,
        delivery_mode=DeliveryMode.PERSISTENT
    )
    await event_logger_exchange.publish(
        routing_message,
        routing_key=EVENT_DATA_TOPIC
    )

async def on_message(message, **kwargs):
    main_exchange = kwargs.get("main_exchange")
    event_logger_exchange = kwargs.get("event_logger_exchange")
    await on_message_print(message)
    await on_message_route_it(message, main_exchange)
    await on_message_log_it(message, event_logger_exchange)
    
async def configure_main_exchange(channel):
    main_exchange = await channel.declare_exchange(MAIN_EXCHANGE, ExchangeType.TOPIC)
    queue = await channel.declare_queue(MAIN_TOPIC, durable=True)
    await queue.bind(main_exchange, routing_key=MAIN_TOPIC)
    
    return main_exchange, queue


async def configure_routing_exchange(channel):
    routing_exchange = await channel.declare_exchange(ROUTING_EXCHANGE, ExchangeType.TOPIC)
    queue = await channel.declare_queue(ROUTING_TOPIC, durable=True)
    await queue.bind(routing_exchange, routing_key=MAIN_TOPIC)
    return routing_exchange


async def configure_event_logger_exchange(channel):
    event_logger_exchange = await channel.declare_exchange(EVENT_DATA_EXCHANGE, ExchangeType.TOPIC)
    queue = await channel.declare_queue(EVENT_DATA_TOPIC, durable=True)
    await queue.bind(event_logger_exchange, routing_key=MAIN_TOPIC)
    return event_logger_exchange


async def main(loop):
    # Perform connection
    connection = await connect(AMQP_URI, loop=loop)

    # Creating a channel
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)

    # Declare an exchange
    main_exchange, queue = await configure_main_exchange(channel)
    routing_exchange = await configure_routing_exchange(channel)
    event_data_exchange = await configure_event_logger_exchange(channel)

    await queue.consume(on_message, arguments=dict(main_exchange=main_exchange, event_logger_exchange=event_data_exchange))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main(loop))

    # we enter a never-ending loop that waits for
    # data and runs callbacks whenever necessary.
    print(" [*] Waiting for messages. To exit press CTRL+C")
    loop.run_forever()