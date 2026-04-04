"""Database connection setup using SQLite (swap to PostgreSQL for Render)."""

import sqlite3
import csv
import os
from app.config import DATABASE_URL, DATA_CSV_PATH

# TODO: Replace with SQLAlchemy if you want a proper ORM layer.
# For now, raw sqlite3 keeps things simple and dependency-free.

_DB_PATH = DATABASE_URL.replace("sqlite:///", "")


def get_connection() -> sqlite3.Connection:
    """Return a new SQLite connection with row_factory set for dict-like rows."""
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create tables and seed data if not already done."""
    conn = get_connection()
    _create_tables(conn)
    _seed_olympic_data(conn)
    conn.close()


def _create_tables(conn: sqlite3.Connection) -> None:
    """Create users and olympics tables."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id   TEXT PRIMARY KEY,
            email     TEXT UNIQUE NOT NULL,
            password  TEXT NOT NULL,
            tokens    INTEGER NOT NULL DEFAULT 100
        );

        CREATE TABLE IF NOT EXISTS olympics (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            athlete   TEXT,
            age       INTEGER,
            country   TEXT,
            year      INTEGER,
            season    TEXT,
            city      TEXT,
            sport     TEXT,
            event     TEXT,
            medal     TEXT
        );
    """)
    conn.commit()


def _seed_olympic_data(conn: sqlite3.Connection) -> None:
    """Load CSV into the olympics table — skips if data already exists."""
    count = conn.execute("SELECT COUNT(*) FROM olympics").fetchone()[0]
    if count > 0:
        return  # already seeded

    if not os.path.exists(DATA_CSV_PATH):
        print(f"[WARNING] CSV not found at {DATA_CSV_PATH} — skipping seed.")
        print("          Download the dataset from Kaggle and place it at that path.")
        return

    # TODO: Map actual CSV column names once you've downloaded the dataset.
    # Expected columns (from Kaggle dataset):
    # Name, Age, Team, Year, Season, City, Sport, Event, Medal
    with open(DATA_CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [
            (r["Name"], r.get("Age"), r["Team"], r["Year"],
             r["Season"], r["City"], r["Sport"], r["Event"], r.get("Medal"))
            for r in reader
        ]

    conn.executemany(
        "INSERT INTO olympics (athlete, age, country, year, season, city, sport, event, medal) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    print(f"[INFO] Seeded {len(rows)} rows from {DATA_CSV_PATH}")
