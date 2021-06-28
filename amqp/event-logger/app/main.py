from typing import Optional
from fastapi import FastAPI
import json
import asyncio
import os
from runner import on_message
from aio_pika import connect
from functools import partial
from runner import on_message
from elasticsearch import Elasticsearch
from starlette_exporter import PrometheusMiddleware, handle_metrics


EVENT_LOGGER_QUEUE = os.environ.get("EVENT_LOGGER_QUEUE", "event_logger")

AMQP_URI = os.environ.get("AMQP_URI",  "amqp://guest:guest@localhost/")
ELASTIC_URI = os.environ.get("ELASTIC_URI",  "0.0.0.0:9200")

app = FastAPI()
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", handle_metrics)


async def main():
    connection = await connect(AMQP_URI)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)
    queue = await channel.declare_queue(EVENT_LOGGER_QUEUE, durable=True)
    es_client = Elasticsearch(ELASTIC_URI, timeout=60)
    await queue.consume(partial(on_message, es_client))


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(main())

@app.get("/")
def read_root():
    return {"Hello": "World"}
