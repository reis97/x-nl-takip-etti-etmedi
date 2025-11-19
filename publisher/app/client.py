# publisher/app/client.py
import os
import requests

X_API_BEARER = os.getenv("X_API_BEARER", "")

def post_to_x(text):
    headers = {"Authorization": f"Bearer {X_API_BEARER}", "Content-Type": "application/json"}
    return requests.post("https://api.x.com/2/tweets", json={"text": text}, headers=headers, timeout=10)
