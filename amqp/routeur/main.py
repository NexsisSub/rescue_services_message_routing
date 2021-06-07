import asyncio
import sys
from aio_pika import connect, IncomingMessage, ExchangeType, Message, DeliveryMode
import os 


ROUTEUR_TOPIC = os.environ.get("ROUTEUR_TOPIC", "routing")
ROUTEUR_EXCHANGE = os.environ.get("ROUTEUR_EXCHANGE", "routing")

ROUTING_EXCHANGE = os.environ.get("ROUTING_EXCHANGE", "event_data")
ROUTING_TOPIC = os.environ.get("ROUTING_TOPIC", "event_data")

AMQP_URI = os.environ.get("AMQP_URI",  "amqp://guest:guest@localhost/")



async def on_message(message: IncomingMessage, routing_exchange):
    with message.process():
        print(" [x] %r:%r" % (message.routing_key, message.body))

    routing_message = Message(
        b"Hellooooo",
        delivery_mode=DeliveryMode.PERSISTENT
    )
    await routing_exchange.publish(
        routing_message,
        routing_key="routing.pompiers-77.cisu"
    )


async def main(loop):
    # Perform connection
    connection = await connect(AMQP_URI, loop=loop)

    # Creating a channel
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)

    # Declare an exchange
    routeur_exchange = await channel.declare_exchange(
        ROUTEUR_EXCHANGE, ExchangeType.TOPIC
    )

        # Declare an exchange
    routing_exchange = await channel.declare_exchange(
        ROUTING_EXCHANGE, ExchangeType.TOPIC
    )

    # Declaring queue
    queue = await channel.declare_queue(ROUTEUR_TOPIC, durable=True)
    await channel.declare_queue(ROUTING_TOPIC, durable=True)
    binding_keys = [ROUTEUR_TOPIC]

    for binding_key in binding_keys:
        await queue.bind(routeur_exchange, routing_key=binding_key)

    # Start listening the queue with name 'task_queue'
    await queue.consume(lambda message : on_message(message, routing_exchange))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main(loop))

    # we enter a never-ending loop that waits for
    # data and runs callbacks whenever necessary.
    print(" [*] Waiting for messages. To exit press CTRL+C")
    loop.run_forever()