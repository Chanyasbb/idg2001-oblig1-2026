"""Token management routes."""

import httpx
from fastapi import APIRouter, HTTPException
from app.models.token import TokenAdd, TokenRedeem
from app.database import queries
from app.config import TOKENS_PER_MONEY, TOKEN_SHOP_URL

router = APIRouter(tags=["tokens"])


@router.post("/tokens", status_code=200)
def add_tokens(body: TokenAdd):
    """POST /v1/tokens — directly add tokens to a user (admin/dev use)."""
    if not queries.get_user(body.user_id):
        raise HTTPException(status_code=404, detail="User not found")
    queries.add_tokens(body.user_id, body.amount)
    user = queries.get_user(body.user_id)
    return {"user_id": body.user_id, "tokens": user["tokens"]}


@router.get("/tokens")
def get_token_price():
    """GET /v1/tokens — return the current token exchange rate."""
    return {"tokens_per_money": TOKENS_PER_MONEY}


@router.post("/tokens/redeem")
def redeem_tokens(body: TokenRedeem):
    """POST /v1/tokens/redeem — verify a one-time code from the token shop and credit tokens.

    Flow: client buys a code from the token shop, then redeems it here.
    The token shop marks the code as used after the first successful redemption.
    """
    if not queries.get_user(body.user_id):
        raise HTTPException(status_code=404, detail="User not found")

    try:
        resp = httpx.get(f"{TOKEN_SHOP_URL}/verify/{body.code}")
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Token shop unavailable")

    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail="Code not found")
    if resp.status_code == 409:
        raise HTTPException(status_code=409, detail="Code already used")
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Unexpected token shop error")

    data = resp.json()
    queries.add_tokens(body.user_id, data["tokens"])
    user = queries.get_user(body.user_id)
    return {"user_id": body.user_id, "tokens": user["tokens"]}
