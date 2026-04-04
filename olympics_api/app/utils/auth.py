"""Authentication helpers — token check middleware and password hashing."""

import hashlib
import uuid
from fastapi import HTTPException, Header
from typing import Optional

from app.database import queries


def hash_password(password: str) -> str:
    """Hash a password with SHA-256. TODO: switch to bcrypt for real security."""
    return hashlib.sha256(password.encode()).hexdigest()


def generate_user_id() -> str:
    """Generate a unique user ID."""
    return str(uuid.uuid4())


def require_tokens(user_id: str) -> None:
    """Check user has tokens and deduct one. Raises 402 if out of tokens.

    Call this at the start of every data endpoint handler.
    """
    success = queries.deduct_token(user_id)
    if not success:
        raise HTTPException(status_code=402, detail="Insufficient tokens")


# TODO: add proper auth (e.g. JWT or API key in header) so user_id isn't
# just passed as a query param. For now it's kept simple.
def get_current_user(x_user_id: Optional[str] = Header(default=None)) -> str:
    """Extract user_id from X-User-Id header. Raises 401 if missing."""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Missing X-User-Id header")
    user = queries.get_user(x_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return x_user_id
