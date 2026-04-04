"""Sport data routes — supports query parameters as required by assignment."""

from fastapi import APIRouter, HTTPException, Depends
from typing import Literal, Optional
from app.database import queries
from app.utils.auth import get_current_user, require_tokens
from app.utils.format import pick_format
from app.models.olympic import EventCreate

router = APIRouter(tags=["sport"])


@router.get("/sport/{sport_id}")
def get_sport(
    sport_id: str,
    country: Optional[str] = None,
    year: Optional[int] = None,
    medals: Optional[str] = None,
    format: Literal["json", "xml"] = "json",
    user_id: str = Depends(get_current_user),
):
    """GET /v1/sport/<sport_id> — results for a sport with optional filters.

    Query params:
        country  — e.g. NOR
        year     — e.g. 2014
        medals   — gold | silver | bronze
        format   — json | xml

    Example: GET /v1/sport/ski-jumping?country=NOR&year=2014&medals=gold
    """
    require_tokens(user_id)
    records = queries.get_sport(sport_id, country=country, year=year, medal=medals)

    if not records:
        return pick_format([], fmt=format, root_tag="sport")

    return pick_format(records, fmt=format, root_tag="sport")


@router.post("/event", status_code=201)
def create_event(
    body: EventCreate,
    user_id: str = Depends(get_current_user),
):
    """POST /v1/event — add a new athlete event/participation row."""
    require_tokens(user_id)
    queries.insert_event(body.model_dump())
    return {"message": "Event created"}
