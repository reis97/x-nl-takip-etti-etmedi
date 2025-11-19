# worker/app/tasks.py
from celery import Celery
import os
import json
import logging
from sqlalchemy import text
from worker.app.db import engine, SessionLocal

logger = logging.getLogger("worker")
BROKER_URL = os.getenv("BROKER_URL", "pyamqp://guest@rabbitmq//")
app = Celery('worker', broker=BROKER_URL)
PUBLISHER_URL = os.getenv("PUBLISHER_URL", "http://publisher:9000")
PUBLISHER_TOKEN = os.getenv("WORKER_PUBLISHER_TOKEN", "pubtoken")

@app.task(bind=True, max_retries=5, default_retry_delay=30)
def process_event(self, raw_event):
    try:
        payload = raw_event.get('payload')
        event_id = raw_event.get('id')
        evt_type = payload.get('event')
        source_id = payload.get('source_user_id')
        target_id = payload.get('target_user_id')

        with engine.begin() as conn:
            # idempotency: try insert into events_log
            res = conn.execute(text("INSERT INTO events_log(event_id, raw_event, processed) VALUES (:eid, :raw, false) ON CONFLICT (event_id) DO NOTHING RETURNING id"), {
                "eid": event_id,
                "raw": json.dumps(payload)
            })
            row = res.fetchone()
            if not row:
                logger.info("Duplicate or already processed event %s", event_id)
                return

        # check previous state
        with engine.begin() as conn:
            cur = conn.execute(text("SELECT is_following FROM celebrity_follows WHERE celeb_user_id=:cid AND target_user_id=:tid"), {"cid": source_id, "tid": target_id}).fetchone()
            prev = cur[0] if cur else None
            new_state = (evt_type == "follow")

            if prev is None:
                conn.execute(text("INSERT INTO celebrity_follows (celeb_user_id, target_user_id, is_following, last_event_id, last_update) VALUES (:cid, :tid, :isf, :eid, now())"), {"cid": source_id, "tid": target_id, "isf": new_state, "eid": event_id})
                changed = True
            else:
                if prev != new_state:
                    conn.execute(text("UPDATE celebrity_follows SET is_following=:isf, last_event_id=:eid, last_update=now() WHERE celeb_user_id=:cid AND target_user_id=:tid"), {"isf": new_state, "eid": event_id, "cid": source_id, "tid": target_id})
                    changed = True
                else:
                    changed = False

        if changed:
            # call publisher
            post_payload = {"celeb_user_id": source_id, "target_user_id": target_id, "is_following": new_state, "event_id": event_id}
            headers = {"Authorization": f"Bearer {PUBLISHER_TOKEN}"}
            import requests
            resp = requests.post(f"{PUBLISHER_URL}/publish", json=post_payload, headers=headers, timeout=10)
            if resp.status_code not in (200,201):
                logger.error("Publisher returned %s %s", resp.status_code, resp.text)
                raise Exception("Publish failed")

        # mark processed
        with engine.begin() as conn:
            conn.execute(text("UPDATE events_log SET processed = true WHERE event_id=:eid"), {"eid": event_id})

    except Exception as e:
        logger.exception("Error processing event")
        raise self.retry(exc=e)
