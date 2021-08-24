from typing import Optional
from fastapi import FastAPI
import json
import asyncio
import os
from runner import on_message, configure_routing_exchange
from aio_pika import connect
from functools import partial
from starlette_exporter import PrometheusMiddleware, handle_metrics
from elasticsearch import Elasticsearch


AMQP_URI = os.environ.get("AMQP_URI",  "amqp://guest:guest@rabbitmq:5672/")
DISTRIBUTION_QUEUE = os.environ.get("DISTRIBUTION_QUEUE", "distribution")
ELASTIC_URI = os.environ.get("ELASTIC_URI",  "0.0.0.0:9200")


app = FastAPI(
    title="Dispatcher",
    description="The dispatcher route every message to specific queues with EDXL receivers",
    version="0.0.1",
)

app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", handle_metrics)


async def main():
    connection = await connect(AMQP_URI)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)
    queue = await channel.declare_queue(DISTRIBUTION_QUEUE, durable=True)
    routing_exchange = await configure_routing_exchange(channel)
    es_client = Elasticsearch(ELASTIC_URI, timeout=60)
    await queue.consume(partial(on_message, channel, routing_exchange, es_client))


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(main())

@app.get("/")
def read_root():
    return {"Hello": "World"}
