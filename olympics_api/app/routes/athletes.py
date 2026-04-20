"""Athlete data routes."""

from fastapi import APIRouter, HTTPException, Depends
from typing import Literal, Optional
from app.database import queries
from app.utils.auth import get_current_user, require_tokens
from app.utils.format import pick_format

router = APIRouter(tags=["athletes"])


@router.get("/athlete/{athlete_id}")
def get_athlete_by_id(
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


@router.get("/athlete")
def search_athletes(
    name: str,
    format: Literal["json", "xml"] = "json",
    user_id: str = Depends(get_current_user),
):
    """GET /v1/athlete?name=<name> — search athletes by name (partial, case-insensitive).

    Example: GET /v1/athlete?name=Usain+Bolt
    """
    require_tokens(user_id)
    records = queries.get_athlete_by_name(name)
    if not records:
        raise HTTPException(status_code=404, detail="No athletes found")
    return pick_format(records, fmt=format, root_tag="athletes")
