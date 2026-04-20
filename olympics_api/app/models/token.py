"""Pydantic models for token operations."""

from pydantic import BaseModel


class TokenAdd(BaseModel):
    """Body for POST /tokens — add tokens to a user (admin use)."""
    user_id: str
    amount: int


class TokenRedeem(BaseModel):
    """Body for POST /tokens/redeem — one-time code from the token shop."""
    user_id: str
    code: str
