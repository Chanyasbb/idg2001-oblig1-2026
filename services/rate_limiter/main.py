"""Rate limiter service — tracks requests per user and returns a delay value.

Formula: delay = r / 10  (where r = requests in last 10 seconds)
Only kicks in when r >= 10.

The Main API calls this before processing each request:
    1. POST /<user_id>  — register the incoming request
    2. GET /<user_id>   — get the delay, then time.sleep(delay)

Endpoints:
    POST /<user_id>   — record a new request timestamp
    GET /<user_id>    — return delay in seconds based on recent request count
"""

import time
from fastapi import FastAPI

app = FastAPI(title="Rate Limiter Service")

WINDOW_SECONDS = 10

# Store per-user request timestamps: { user_id: [timestamp, ...] }
_request_log: dict[str, list[float]] = {}


def _clean_old(user_id: str) -> list[float]:
    """Remove timestamps older than WINDOW_SECONDS and return the remaining list."""
    now = time.time()
    recent = [t for t in _request_log.get(user_id, []) if now - t <= WINDOW_SECONDS]
    _request_log[user_id] = recent
    return recent


@app.post("/{user_id}")
def record_request(user_id: str):
    """Record a new request timestamp for this user."""
    if user_id not in _request_log:
        _request_log[user_id] = []
    _request_log[user_id].append(time.time())
    return {"recorded": True}


@app.get("/{user_id}")
def get_delay(user_id: str) -> dict:
    """Return how many seconds the Main API should sleep before responding."""
    recent = _clean_old(user_id)
    r = len(recent)

    # f(r) = r / 10, but only apply when r >= 10
    delay = r / 10 if r >= 10 else 0.0

    return {"delay": delay, "requests_in_window": r}
