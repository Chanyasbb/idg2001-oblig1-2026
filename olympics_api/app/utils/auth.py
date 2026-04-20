"""Authentication helpers — password hashing and user identity from headers."""

import uuid
import bcrypt
from fastapi import HTTPException, Header
from typing import Optional

from app.database import queries
from app.utils.token_cost import COST_DEFAULT


def hash_password(password: str) -> str:
    """Hash a password with bcrypt (auto-salted, one-way)."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Check a plaintext password against a stored bcrypt hash."""
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def generate_user_id() -> str:
    """Generate a collision-resistant user ID (UUID4)."""
    return str(uuid.uuid4())


def require_tokens(user_id: str, cost: int = COST_DEFAULT) -> None:
    """Deduct `cost` tokens from the user. Raises 402 if balance is too low.

    Call at the start of every billable endpoint handler.
    """
    if not queries.deduct_tokens(user_id, cost):
        raise HTTPException(status_code=402, detail="Insufficient tokens")


def get_current_user(x_user_id: Optional[str] = Header(default=None)) -> str:
    """Extract user identity from the X-User-Id request header.

    Raises 401 if the header is absent, 404 if the user does not exist.
    """
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Missing X-User-Id header")
    if not queries.get_user(x_user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return x_user_id
