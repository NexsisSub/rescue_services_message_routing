from typing import Optional
from fastapi import FastAPI
import json
import asyncio
import os
from runner import on_message
from aio_pika import connect
from functools import partial
from runner import on_message, configure_errors_exchange
from starlette_exporter import PrometheusMiddleware, handle_metrics


DLX_QUEUE = os.environ.get("DLX_QUEUE", "dlx_queue")

AMQP_URI = os.environ.get("AMQP_URI",  "amqp://guest:guest@rabbitmq:5672/")

PROTOCOLS = os.environ.get("PROTOCOLS", "cisu/emsi").split("/")

app = FastAPI(
    title="Errors Worker",
    description="This worker handle DLX queue",
    version="0.0.1",
)
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", handle_metrics)


async def main():    
    print("starting main ")
    connection = await connect(AMQP_URI)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)
    
    errors_exchange = await configure_errors_exchange(channel)

    for protocol in PROTOCOLS: 
        queue = await channel.declare_queue(f"{DLX_QUEUE}.{protocol}", durable=True)
        await queue.consume(partial(on_message, channel, errors_exchange))

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(main())

@app.get("/")
def read_root():
    return {"Hello": "World"}
