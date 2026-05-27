"""Token management routes."""

from fastapi import APIRouter, HTTPException
from app.models.token import TokenAdd
from app.database import queries

router = APIRouter(tags=["tokens"])


@router.post("/tokens", status_code=200)
def add_tokens(body: TokenAdd):
    """POST /v1/tokens — directly add tokens to a user (admin/dev use)."""
    if not queries.get_user(body.user_id):
        raise HTTPException(status_code=404, detail="User not found")
    queries.add_tokens(body.user_id, body.amount)
    user = queries.get_user(body.user_id)
    return {"user_id": body.user_id, "tokens": user["tokens"]}
