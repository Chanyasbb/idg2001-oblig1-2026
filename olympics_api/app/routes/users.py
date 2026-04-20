"""User management routes — CRUD for /v1/user endpoints."""

from fastapi import APIRouter, HTTPException
from app.models.user import UserCreate, UserUpdate, UserResponse
from app.database import queries
from app.utils.auth import hash_password, generate_user_id
from app.config import DEFAULT_TOKEN_AMOUNT

router = APIRouter(tags=["users"])


@router.post("/user", response_model=UserResponse, status_code=201)
def create_user(body: UserCreate):
    """POST /v1/user — register a new user with default tokens."""
    if queries.get_user_by_email(body.email):
        raise HTTPException(status_code=409, detail="Email already registered")

    user_id = generate_user_id()
    hashed = hash_password(body.password)
    queries.create_user(user_id, body.email, hashed, DEFAULT_TOKEN_AMOUNT)
    return {"user_id": user_id, "email": body.email, "tokens": DEFAULT_TOKEN_AMOUNT}


@router.get("/user", response_model=list[UserResponse])
def get_users():
    """GET /v1/user — list all users."""
    return queries.get_all_users()


@router.get("/user/{user_id}", response_model=UserResponse)
def get_user(user_id: str):
    """GET /v1/user/<user_id> — fetch a single user."""
    user = queries.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/user/{user_id}", response_model=UserResponse)
@router.patch("/user/{user_id}", response_model=UserResponse)
def update_user(user_id: str, body: UserUpdate):
    """PUT|PATCH /v1/user/<user_id> — update email and/or password."""
    if not queries.get_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")

    fields = {}
    if body.email:
        fields["email"] = body.email
    if body.password:
        fields["password"] = hash_password(body.password)

    if fields:
        queries.update_user(user_id, fields)

    return queries.get_user(user_id)


@router.delete("/user/{user_id}", status_code=204)
def delete_user(user_id: str):
    """DELETE /v1/user/<user_id> — remove a user."""
    if not queries.get_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    queries.delete_user(user_id)
