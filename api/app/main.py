from typing import Optional
from nats.aio.client import Client as NATS
from fastapi import FastAPI
import json
import asyncio


app = FastAPI()
nc = NATS()

ROUTEUR_SUBJECT = os.environ.get("ROUTEUR_SUBJECT", "routing")

async def error_cb(e):
    print("Error:", e)

async def closed_cb():
    print("Connection to NATS is closed.")

async def reconnected_cb():
    print(f"Connected to NATS at {nc.connected_url.netloc}...")



@app.on_event("startup")
async def startup_event():
    options = {
        "servers":["nats://nats:4222"],
        "error_cb": error_cb,
        "closed_cb": closed_cb,
        "reconnected_cb": reconnected_cb
    }

    await nc.connect(**options)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/echange")
async def read_root():
    await nc.publish(ROUTEUR_SUBJECT, json.dumps({"destinataires": ["pompiers-77", "samu-77"] }).encode())

    return {"Hello": "Send"}

