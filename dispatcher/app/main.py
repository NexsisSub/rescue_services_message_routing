from typing import Optional
from fastapi import FastAPI
import json
import asyncio
import os
from runner import on_message, configure_routing_exchange, wait_for_rabbitmq_startup
from aio_pika import connect
from functools import partial
from starlette_exporter import PrometheusMiddleware, handle_metrics
from database import SessionLocal
from models import Base
from database import engine


AMQP_URI = os.environ.get("AMQP_URI",  "amqp://guest:guest@rabbitmq:5672/")
DISTRIBUTION_QUEUE = os.environ.get("DISTRIBUTION_QUEUE", "distribution")


app = FastAPI(
    title="Dispatcher",
    description="The dispatcher route every message to specific queues with EDXL receivers",
    version="0.0.1",
)

app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", handle_metrics)


Base.metadata.create_all(bind=engine)

async def main():
    await wait_for_rabbitmq_startup(AMQP_URI)
    connection = await connect(AMQP_URI)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)
    queue = await channel.declare_queue(DISTRIBUTION_QUEUE, durable=True)
    routing_exchange = await configure_routing_exchange(channel)
    db = SessionLocal()
    await queue.consume(partial(on_message, channel, routing_exchange, db))


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(main())

@app.get("/")
def read_root():
    return {"Hello": "World"}
