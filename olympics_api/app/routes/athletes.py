"""Athlete data routes."""

from fastapi import APIRouter, HTTPException, Depends
from typing import Literal
from app.database import queries
from app.utils.auth import get_current_user, require_tokens
from app.utils.format import pick_format

router = APIRouter(tags=["athletes"])


@router.get("/athlete/{athlete_id}")
def get_athlete(
    athlete_id: int,
    format: Literal["json", "xml"] = "json",
    user_id: str = Depends(get_current_user),
):
    """GET /v1/athlete/<athlete_id> — fetch a single athlete record by row ID."""
    require_tokens(user_id)
    record = queries.get_athlete(athlete_id)
    if not record:
        raise HTTPException(status_code=404, detail="Athlete not found")
    return pick_format(record, fmt=format, root_tag="athlete")


# TODO: also support searching by name?
# GET /v1/athlete?name=Usain+Bolt
