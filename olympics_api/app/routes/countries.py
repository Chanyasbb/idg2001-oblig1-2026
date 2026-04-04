"""Country data routes."""

from fastapi import APIRouter, HTTPException, Depends
from typing import Literal
from app.database import queries
from app.utils.auth import get_current_user, require_tokens
from app.utils.format import pick_format

router = APIRouter(tags=["countries"])


@router.get("/country/{country_id}")
def get_country(
    country_id: str,
    format: Literal["json", "xml"] = "json",
    user_id: str = Depends(get_current_user),
):
    """GET /v1/country/<country_id> — all results for a country (e.g. 'NOR').

    Returns medal counts grouped by sport.
    """
    require_tokens(user_id)
    records = queries.get_country(country_id)
    if not records:
        raise HTTPException(status_code=404, detail="Country not found")

    # Group by sport and count medals
    grouped: dict = {}
    for r in records:
        sport = r["sport"]
        if sport not in grouped:
            grouped[sport] = {"gold": 0, "silver": 0, "bronze": 0, "na": 0, "total": 0}
        medal = (r["medal"] or "").lower()
        if medal == "gold":
            grouped[sport]["gold"] += 1
        elif medal == "silver":
            grouped[sport]["silver"] += 1
        elif medal == "bronze":
            grouped[sport]["bronze"] += 1
        else:
            grouped[sport]["na"] += 1
        grouped[sport]["total"] += 1

    return pick_format(grouped, fmt=format, root_tag="country")
