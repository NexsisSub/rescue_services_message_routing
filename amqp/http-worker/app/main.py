from typing import Optional
from fastapi import FastAPI
import json
import asyncio
import os
from runner import on_message
from aio_pika import connect
from functools import partial
from parser import parse_subsucriptions
from runner import on_message, wait_for_rabbitmq_startup
from starlette_exporter import PrometheusMiddleware, handle_metrics


DLX_QUEUE = os.environ.get("DLX_QUEUE", "dlx_queue")

AMQP_URI = os.environ.get("AMQP_URI",  "amqp://guest:guest@rabbitmq:5672/")

PROTOCOLS = os.environ.get("PROTOCOLS", "cisu/emsi").split("/")

app = FastAPI(
    title="Http Worker",
    description="This worker handle http requests",
    version="0.0.1",
)

app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", handle_metrics)

subscriptions = parse_subsucriptions()

async def main():    
    print("starting main ")
    await wait_for_rabbitmq_startup(AMQP_URI)
    connection = await connect(AMQP_URI)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)
    for protocol in PROTOCOLS: 
        queue = await channel.declare_queue(f"routing.all.{protocol}", durable=True)
        await queue.consume(partial(on_message, subscriptions))

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(main())

@app.get("/")
def read_root():
    return {"Hello": "World"}
