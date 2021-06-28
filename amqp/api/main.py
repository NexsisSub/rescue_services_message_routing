import asyncio
import tornado.ioloop
import tornado.web
import os
from aio_pika import connect_robust, Message, ExchangeType
from tornado import gen

tornado.ioloop.IOLoop.configure("tornado.platform.asyncio.AsyncIOLoop")
io_loop = tornado.ioloop.IOLoop.current()
asyncio.set_event_loop(io_loop.asyncio_loop)

DISTRIBUTION_EXCHANGE = os.environ.get("MAIN_EXCHANGE", "distribution")
DISTRIBUTION_ROUTING_KEY = os.environ.get("DISTRIBUTION_ROUTING_KEY", "distribution")
DISTRIBUTION_QUEUE = os.environ.get("DISTRIBUTION_QUEUE", "distribution")
ROUTING_EXCHANGE = os.environ.get("ROUTING_EXCHANGE", "routing")


QUEUE = asyncio.Queue()


class PublisherHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def post(self):
        connection = self.application.settings["amqp_connection"]
        channel = yield connection.channel()
        distribution_exchange = yield channel.declare_exchange(DISTRIBUTION_EXCHANGE, ExchangeType.TOPIC)
        distribution_queue = yield channel.declare_queue(DISTRIBUTION_QUEUE, durable=True)
        try:
            yield distribution_exchange.publish(
                Message(body=self.request.body), routing_key=DISTRIBUTION_ROUTING_KEY,
            )
        finally:
            yield channel.close()

        self.finish("OK")


async def make_app():
    amqp_connection = await connect_robust()

    channel = await amqp_connection.channel()
    distribution_exchange = await channel.declare_exchange(DISTRIBUTION_EXCHANGE, ExchangeType.TOPIC)
    distribution_queue = await channel.declare_queue(DISTRIBUTION_QUEUE, durable=True)

    return tornado.web.Application(
        [(r"/publish", PublisherHandler)],
        amqp_connection=amqp_connection,
    )


if __name__ == "__main__":
    app = io_loop.asyncio_loop.run_until_complete(make_app())
    app.listen(8888)

    tornado.ioloop.IOLoop.current().start()