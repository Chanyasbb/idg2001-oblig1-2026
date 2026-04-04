"""Pydantic models for token operations."""

from pydantic import BaseModel


class TokenAdd(BaseModel):
    """Body for POST /tokens — add tokens to a user."""
    user_id: str
    amount: int


class TokenRedeem(BaseModel):
    """Body for redeeming a token-shop code (Assignment 2)."""
    code: str
