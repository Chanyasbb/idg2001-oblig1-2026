"""Token shop service — handles fake token purchases with one-time secret codes.

Flow:
    1. Client → POST /buy (with username + money amount)
    2. Token shop → returns { "secret": "<code>" }
    3. Client → POST /v1/tokens/redeem on Main API with the code
    4. Main API → GET /verify/<code> here to get token amount
    5. Token shop marks code as used (prevents double-spending)

Endpoints:
    POST /buy            — "purchase" tokens, get a secret code back
    GET  /verify/<code>  — Main API calls this to redeem a code
"""

import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Token Shop Service")

# In-memory store of active codes: { code: {"username": str, "tokens": int, "used": bool} }
_codes: dict[str, dict] = {}

# How many tokens 1 "money" unit buys — Main API can update this via config
TOKENS_PER_MONEY = 10


class BuyRequest(BaseModel):
    username: str
    money: int   # how many "money" units to spend


@app.post("/buy")
def buy_tokens(body: BuyRequest):
    """Generate a one-time secret code for a token purchase."""
    if body.money <= 0:
        raise HTTPException(status_code=400, detail="money must be > 0")

    code = str(uuid.uuid4())
    tokens = body.money * TOKENS_PER_MONEY
    _codes[code] = {"username": body.username, "tokens": tokens, "used": False}

    return {"secret": code}


@app.get("/verify/{code}")
def verify_code(code: str):
    """Main API calls this to redeem a code. Marks code as used after first call."""
    entry = _codes.get(code)
    if not entry:
        raise HTTPException(status_code=404, detail="Code not found")
    if entry["used"]:
        raise HTTPException(status_code=409, detail="Code already used")

    # Mark as used to prevent double-spending
    _codes[code]["used"] = True

    return {"tokens": entry["tokens"], "username": entry["username"]}
