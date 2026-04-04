"""App-wide configuration — reads from environment variables.

Load env before starting:
    Dev:  uvicorn app.main:app --reload  (with --env-file=../.env.dev)
    Prod: uvicorn app.main:app           (with --env-file=../.env.prod)

Or use python-dotenv to load automatically (see below).
"""

import os
from dotenv import load_dotenv

# Load .env.dev by default; override with ENV=prod to load .env.prod
_env = os.getenv("ENV", "dev")
load_dotenv(dotenv_path=f"../.env.{_env}")

# --- Database ---
# Using SQLite for local dev. For Render, switch to PostgreSQL and set DATABASE_URL.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./olympics.db")

# Path to the Olympics CSV dataset (loaded into DB on startup)
DATA_CSV_PATH = os.getenv("DATA_CSV_PATH", "data/olympic.csv")

# --- Token system ---
DEFAULT_TOKEN_AMOUNT = int(os.getenv("DEFAULT_TOKENS", "100"))  # tokens given on signup
TOKENS_PER_MONEY = int(os.getenv("TOKENS_PER_MONEY", "10"))     # tokens per 1 "money" unit

# --- Assignment 2: microservice URLs ---
# Only used when running full Docker Compose. Ignored in standalone Assignment 1 mode.
CACHE_URL = os.getenv("CACHE_URL", "http://cache:8001")
LOGGER_URL = os.getenv("LOGGER_URL", "http://logger:8002")
RATE_LIMITER_URL = os.getenv("RATE_LIMITER_URL", "http://rate_limiter:8003")
TOKEN_SHOP_URL = os.getenv("TOKEN_SHOP_URL", "http://token_shop:8004")
