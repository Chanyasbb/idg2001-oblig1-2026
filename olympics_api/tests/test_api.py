"""API endpoint tests — uses FastAPI TestClient (no live server needed).

Run with: pytest tests/test_api.py
"""

import pytest


# ── health ────────────────────────────────────────────────────────────────────

def test_root_returns_ok(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Olympics API" in resp.json()["message"]


# ── user CRUD ─────────────────────────────────────────────────────────────────

def test_create_user(client):
    """POST /v1/user returns 201 with the new user's data."""
    resp = client.post("/v1/user", json={"email": "test@example.com", "password": "pass123"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "test@example.com"
    assert data["tokens"] == 100
    assert "user_id" in data


def test_duplicate_email_rejected(client):
    """Creating two users with the same email returns 409."""
    payload = {"email": "dup@example.com", "password": "abc"}
    client.post("/v1/user", json=payload)
    resp = client.post("/v1/user", json=payload)
    assert resp.status_code == 409


def test_get_all_users(client):
    """GET /v1/user returns a list."""
    resp = client.get("/v1/user")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_get_user_by_id(client):
    """GET /v1/user/<id> returns the correct user."""
    r = client.post("/v1/user", json={"email": "getme@example.com", "password": "x"})
    uid = r.json()["user_id"]
    resp = client.get(f"/v1/user/{uid}")
    assert resp.status_code == 200
    assert resp.json()["user_id"] == uid


def test_get_unknown_user_returns_404(client):
    resp = client.get("/v1/user/does-not-exist")
    assert resp.status_code == 404


def test_delete_user(client):
    """DELETE /v1/user/<id> returns 204 and the user is gone."""
    r = client.post("/v1/user", json={"email": "delete_me@example.com", "password": "x"})
    uid = r.json()["user_id"]
    assert client.delete(f"/v1/user/{uid}").status_code == 204
    assert client.get(f"/v1/user/{uid}").status_code == 404


# ── token management ──────────────────────────────────────────────────────────

def test_add_tokens_increases_balance(client):
    """POST /v1/tokens adds the specified amount to the user's balance."""
    r = client.post("/v1/user", json={"email": "addtokens@example.com", "password": "p"})
    uid = r.json()["user_id"]
    resp = client.post("/v1/tokens", json={"user_id": uid, "amount": 50})
    assert resp.status_code == 200
    assert resp.json()["tokens"] == 150


def test_tokens_deducted_on_data_endpoint(client):
    """Each data endpoint call costs 1 token — even on 404 (you paid to query)."""
    r = client.post("/v1/user", json={"email": "tokencost@example.com", "password": "p"})
    uid = r.json()["user_id"]
    initial = r.json()["tokens"]

    # athlete/1 will 404 (empty DB), but the token is charged before the lookup
    client.get("/v1/athlete/1", headers={"X-User-Id": uid})
    updated = client.get(f"/v1/user/{uid}").json()
    assert updated["tokens"] == initial - 1


def test_get_token_price(client):
    resp = client.get("/v1/tokens")
    assert resp.status_code == 200
    assert "tokens_per_money" in resp.json()


# ── auth guards ───────────────────────────────────────────────────────────────

def test_missing_auth_header_returns_401(client):
    """Data endpoints require X-User-Id — missing header returns 401."""
    resp = client.get("/v1/athlete/1")
    assert resp.status_code == 401


def test_unknown_user_in_header_returns_404(client):
    resp = client.get("/v1/athlete/1", headers={"X-User-Id": "ghost-id"})
    assert resp.status_code == 404
