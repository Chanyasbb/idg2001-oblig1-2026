"""Cache service — stores GET responses for 1 minute to avoid redundant DB queries.

Architecture (Assignment 2):
    Versioning → Cache → Main API

The Main API calls this service BEFORE querying its own DB.
If a fresh cache entry exists, it returns that. Otherwise Main API queries DB
and then POSTs the result here to cache it.
"""

import time
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Optional

app = FastAPI(title="Cache Service")

# In-memory store: { "endpoint_key": {"data": ..., "timestamp": float} }
_cache: dict[str, dict] = {}

CACHE_TTL_SECONDS = 60  # 1 minute


class CacheEntry(BaseModel):
    key: str       # e.g. "/v1/athlete/123"
    data: Any      # the response data to cache


class CacheLookup(BaseModel):
    key: str


# TODO: consider adding a background task that cleans up expired entries
# instead of doing it on every request.

def _purge_expired() -> None:
    """Delete all entries older than TTL."""
    now = time.time()
    expired = [k for k, v in _cache.items() if now - v["timestamp"] > CACHE_TTL_SECONDS]
    for k in expired:
        del _cache[k]


@app.post("/cache")
def set_cache(entry: CacheEntry):
    """Store a response in cache."""
    _cache[entry.key] = {"data": entry.data, "timestamp": time.time()}
    return {"stored": True}


@app.get("/cache")
def get_cache(key: str) -> dict:
    """Look up a cached response. Returns hit=False if missing or expired."""
    _purge_expired()
    entry = _cache.get(key)
    if not entry:
        return {"hit": False, "data": None}
    return {"hit": True, "data": entry["data"]}


@app.delete("/cache")
def clear_cache():
    """Clear all cached entries (admin use)."""
    _cache.clear()
    return {"cleared": True}
