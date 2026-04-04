"""Versioning / proxy service — sits in front of the cache and routes by API version.

Architecture:
    Client → Versioning → Cache → Main API

This service forwards requests to the correct backend version.
For now there's only v1, so it's mostly a passthrough.
When v2 is added, routing logic goes here.

TODO: This service spec is marked as "(?? Versioning-thingy)" in the assignment —
      check with the teacher what exactly is expected before implementing fully.
"""

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import Response
import os

app = FastAPI(title="Versioning Service")

CACHE_URL = os.getenv("CACHE_URL", "http://cache:8001")
MAIN_API_URL = os.getenv("MAIN_API_URL", "http://main_api:8000")


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(path: str, request: Request):
    """Forward all requests through cache → main API."""
    # TODO: implement version routing here if/when v2 is added
    # For now just forward to main API (cache is handled by main API itself)

    url = f"{MAIN_API_URL}/{path}"
    method = request.method
    headers = dict(request.headers)
    body = await request.body()
    params = dict(request.query_params)

    async with httpx.AsyncClient() as client:
        resp = await client.request(method, url, headers=headers, content=body, params=params)

    return Response(
        content=resp.content,
        status_code=resp.status_code,
        media_type=resp.headers.get("content-type"),
    )
