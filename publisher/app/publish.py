# publisher/app/publish.py
from fastapi import FastAPI, Request, Header, HTTPException
import os
import requests
from datetime import datetime
import logging

app = FastAPI()
logger = logging.getLogger("publisher")
X_API_BEARER = os.getenv("X_API_BEARER", "")
ALLOWED_TOKEN = os.getenv("WORKER_PUBLISHER_TOKEN", "pubtoken")

@app.post("/publish")
async def publish(req: Request, authorization: str = Header(None)):
    if authorization != f"Bearer {ALLOWED_TOKEN}":
        raise HTTPException(status_code=401, detail="unauthorized")

    data = await req.json()
    is_following = data.get("is_following")
    celeb = data.get("celeb_user_id")
    target = data.get("target_user_id")
    event_id = data.get("event_id")

    text = f"🔔 {celeb} artık {target} hesabını {'takip ediyor' if is_following else 'takip etmiyor'}. Tarih: {datetime.utcnow().isoformat()}"

    headers = {"Authorization": f"Bearer {X_API_BEARER}", "Content-Type": "application/json"}
    # Adjust endpoint per X API docs / versions
    resp = requests.post("https://api.x.com/2/tweets", json={"text": text}, headers=headers, timeout=10)
    if resp.status_code not in (200,201):
        logger.error("Failed to publish to X: %s %s", resp.status_code, resp.text)
        raise HTTPException(status_code=500, detail="publish failed")

    return {"status": "ok", "published": True}
