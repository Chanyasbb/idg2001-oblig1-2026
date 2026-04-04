"""Pydantic models for User requests and responses."""

from pydantic import BaseModel
from typing import Optional


class UserCreate(BaseModel):
    """Body for POST /user."""
    email: str
    password: str


class UserUpdate(BaseModel):
    """Body for PUT/PATCH /user/<id> — all fields optional."""
    email: Optional[str] = None
    password: Optional[str] = None


class UserResponse(BaseModel):
    """What we return to the client — never expose password."""
    user_id: str
    email: str
    tokens: int
