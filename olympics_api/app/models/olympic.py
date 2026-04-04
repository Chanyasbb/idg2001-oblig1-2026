"""Pydantic models for Olympic event data."""

from pydantic import BaseModel
from typing import Optional


class EventCreate(BaseModel):
    """Body for POST /event — add a new athlete participation."""
    athlete: str
    age: Optional[int] = None
    country: str
    year: int
    season: str
    city: str
    sport: str
    event: str
    medal: Optional[str] = None  # "Gold", "Silver", "Bronze", or None


class OlympicRecord(BaseModel):
    """A single row from the olympics table."""
    id: int
    athlete: str
    age: Optional[int]
    country: str
    year: int
    season: str
    city: str
    sport: str
    event: str
    medal: Optional[str]
