# receiver/app/main.py
from fastapi import FastAPI, Request, Header, HTTPException
import hmac
import hashlib
import os
import json
from datetime import datetime
import aio_pika
import asyncio
import logging

app = FastAPI()
logger = logging.getLogger("receiver")

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "change-me")
QUEUE_NAME = os.getenv("EVENT_QUEUE", "events_queue")

async def get_rabbit_connection():
    return await aio_pika.connect_robust(RABBITMQ_URL)

async def publish_to_queue(message: dict):
    conn = await get_rabbit_connection()
    async with conn:
        channel = await conn.channel()
        await channel.declare_queue(QUEUE_NAME, durable=True)
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(message).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            ),
            routing_key=QUEUE_NAME
        )

def verify_signature(body: bytes, signature: str) -> bool:
    mac = hmac.new(WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(mac, signature)

@app.post("/x-events")
async def x_events(request: Request, x_x_signature: str = Header(None)):
    body = await request.body()
    if x_x_signature is None or not verify_signature(body, x_x_signature):
        logger.warning("Invalid signature or missing header")
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()
    # Basic validation
    if "event" not in payload:
        raise HTTPException(status_code=400, detail="Bad payload")

    event = {
        "id": payload.get("id") or f"evt-{datetime.utcnow().timestamp()}",
        "received_at": datetime.utcnow().isoformat(),
        "payload": payload
    }

    # Push to queue for processing
    try:
        await publish_to_queue(event)
    except Exception as e:
        logger.exception("Failed to publish event to queue")
        raise HTTPException(status_code=500, detail="Failed to enqueue event")

    return {"status": "accepted"}
