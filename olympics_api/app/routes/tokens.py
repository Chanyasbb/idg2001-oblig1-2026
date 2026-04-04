"""Token management routes."""

from fastapi import APIRouter, HTTPException
from app.models.token import TokenAdd, TokenRedeem
from app.database import queries
from app.config import TOKENS_PER_MONEY

router = APIRouter(tags=["tokens"])


@router.post("/tokens", status_code=200)
def add_tokens(body: TokenAdd):
    """POST /v1/tokens — directly add tokens to a user (admin use)."""
    if not queries.get_user(body.user_id):
        raise HTTPException(status_code=404, detail="User not found")
    queries.add_tokens(body.user_id, body.amount)
    user = queries.get_user(body.user_id)
    return {"user_id": body.user_id, "tokens": user["tokens"]}


@router.get("/tokens")
def get_token_price():
    """GET /v1/tokens — return current token price (tokens per 1 money unit)."""
    return {"tokens_per_money": TOKENS_PER_MONEY}


# TODO (Assignment 2): POST /v1/tokens/redeem — take a secret code from the
# token shop, verify it with the token shop service, and credit tokens.
# @router.post("/tokens/redeem")
# def redeem_tokens(body: TokenRedeem):
#     ...
