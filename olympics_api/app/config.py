"""App-wide configuration — reads from environment variables."""

import os
from pathlib import Path
from dotenv import load_dotenv

_root = Path(__file__).resolve().parent.parent.parent
_env = os.getenv("ENV", "dev")
load_dotenv(dotenv_path=_root / f".env.{_env}", override=False)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./olympics.db")
DATA_CSV_PATH = os.getenv("DATA_CSV_PATH", "data/athlete_events.csv")

DEFAULT_TOKEN_AMOUNT = int(os.getenv("DEFAULT_TOKENS", "100"))
TOKENS_PER_MONEY = int(os.getenv("TOKENS_PER_MONEY", "10"))
