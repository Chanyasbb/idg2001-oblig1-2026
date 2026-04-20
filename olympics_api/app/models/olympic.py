"""Pydantic models for Olympic event data.

Columns mirror the Kaggle 'athlete_events.csv' dataset:
ID, Name, Sex, Age, Height, Weight, Team, NOC, Games, Year, Season, City, Sport, Event, Medal
"""

from pydantic import BaseModel
from typing import Optional


class EventCreate(BaseModel):
    """Body for POST /event — add a new athlete participation row."""
    athlete: str
    sex: Optional[str] = None
    age: Optional[int] = None
    height: Optional[int] = None
    weight: Optional[int] = None
    team: Optional[str] = None
    noc: str
    games: Optional[str] = None
    year: int
    season: str
    city: str
    sport: str
    event: str
    medal: Optional[str] = None  # "Gold", "Silver", "Bronze", or None


class OlympicRecord(BaseModel):
    """A single row from the olympics table."""
    id: int
    athlete: Optional[str]
    sex: Optional[str]
    age: Optional[int]
    height: Optional[int]
    weight: Optional[int]
    team: Optional[str]
    noc: Optional[str]
    games: Optional[str]
    year: Optional[int]
    season: Optional[str]
    city: Optional[str]
    sport: Optional[str]
    event: Optional[str]
    medal: Optional[str]
