"""App-wide configuration — reads from environment variables.

Env files live at the project root (one level above olympics_api/).
python-dotenv resolves the path relative to this file, not the CWD,
so this works regardless of where uvicorn is launched from.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Project root is three levels up from this file:
# config.py → app/ → olympics_api/ → idg2001-oblig1/
_root = Path(__file__).resolve().parent.parent.parent
_env = os.getenv("ENV", "dev")
# override=False: Docker env vars (set via docker-compose) take precedence
load_dotenv(dotenv_path=_root / f".env.{_env}", override=False)

# --- Database ---
# Using SQLite for local dev. For Render, switch to PostgreSQL and set DATABASE_URL.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./olympics.db")

# Path to the Olympics CSV dataset (loaded into DB on startup)
DATA_CSV_PATH = os.getenv("DATA_CSV_PATH", "data/athlete_events.csv")

# --- Token system ---
DEFAULT_TOKEN_AMOUNT = int(os.getenv("DEFAULT_TOKENS", "100"))  # tokens given on signup
TOKENS_PER_MONEY = int(os.getenv("TOKENS_PER_MONEY", "10"))     # tokens per 1 "money" unit

# --- Assignment 2: microservice URLs ---
# Only used when running full Docker Compose. Ignored in standalone Assignment 1 mode.
CACHE_URL = os.getenv("CACHE_URL", "http://cache:8001")
LOGGER_URL = os.getenv("LOGGER_URL", "http://logger:8002")
RATE_LIMITER_URL = os.getenv("RATE_LIMITER_URL", "http://rate_limiter:8003")
TOKEN_SHOP_URL = os.getenv("TOKEN_SHOP_URL", "http://token_shop:8004")
