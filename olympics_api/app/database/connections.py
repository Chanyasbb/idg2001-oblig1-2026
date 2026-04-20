"""Database connection setup — SQLite for dev, swap DATABASE_URL for PostgreSQL on Render."""

import sqlite3
import csv
import os
from app.config import DATABASE_URL, DATA_CSV_PATH

_DB_PATH = DATABASE_URL.replace("sqlite:///", "")


def get_connection() -> sqlite3.Connection:
    """Return a new SQLite connection with dict-like row access."""
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create tables and seed data from CSV on first run."""
    conn = get_connection()
    _create_tables(conn)
    _seed_olympic_data(conn)
    conn.close()


def _create_tables(conn: sqlite3.Connection) -> None:
    """Create the users and olympics tables if they don't exist."""
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
            sex       TEXT,
            age       INTEGER,
            height    INTEGER,
            weight    INTEGER,
            team      TEXT,
            noc       TEXT,
            games     TEXT,
            year      INTEGER,
            season    TEXT,
            city      TEXT,
            sport     TEXT,
            event     TEXT,
            medal     TEXT
        );
    """)
    conn.commit()


def _na(value: str) -> object:
    """Convert Kaggle's 'NA' sentinel to None so it stores as SQL NULL."""
    return None if str(value).strip() in ("NA", "") else value


def _seed_olympic_data(conn: sqlite3.Connection) -> None:
    """Load athlete_events.csv into the olympics table — skips if data already exists.

    CSV columns: ID, Name, Sex, Age, Height, Weight, Team, NOC,
                 Games, Year, Season, City, Sport, Event, Medal
    """
    count = conn.execute("SELECT COUNT(*) FROM olympics").fetchone()[0]
    if count > 0:
        return  # already seeded

    if not os.path.exists(DATA_CSV_PATH):
        print(f"[WARNING] CSV not found at {DATA_CSV_PATH} — skipping seed.")
        print("          Download athlete_events.csv from Kaggle and place it there.")
        return

    with open(DATA_CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [
            (
                r["Name"], r["Sex"],
                _na(r["Age"]), _na(r["Height"]), _na(r["Weight"]),
                r["Team"], r["NOC"], r["Games"],
                r["Year"], r["Season"], r["City"],
                r["Sport"], r["Event"],
                _na(r["Medal"]),  # "NA" → NULL; "Gold"/"Silver"/"Bronze" kept as-is
            )
            for r in reader
        ]

    conn.executemany(
        "INSERT INTO olympics "
        "(athlete, sex, age, height, weight, team, noc, games, "
        "year, season, city, sport, event, medal) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    print(f"[INFO] Seeded {len(rows)} rows from {DATA_CSV_PATH}")
