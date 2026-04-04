"""Reusable DB query helpers — keeps route files clean."""

from typing import Optional
from app.database.connections import get_connection


# --- Olympic data queries ---

def get_athlete(athlete_id: int) -> Optional[dict]:
    """Fetch all records for a given athlete row id."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM olympics WHERE id = ?", (athlete_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_athlete_by_name(name: str) -> list[dict]:
    """Fetch all records for an athlete by name (case-insensitive partial match)."""
    # TODO: decide whether to use exact or fuzzy matching
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM olympics WHERE LOWER(athlete) LIKE ?", (f"%{name.lower()}%",)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_country(country_code: str) -> list[dict]:
    """Fetch all records for a country (team code, e.g. 'NOR')."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM olympics WHERE UPPER(country) = ?", (country_code.upper(),)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_sport(sport_id: str, country: Optional[str] = None,
              year: Optional[int] = None, medal: Optional[str] = None) -> list[dict]:
    """Fetch sport records with optional query filters."""
    query = "SELECT * FROM olympics WHERE LOWER(sport) = ?"
    params: list = [sport_id.lower()]

    if country:
        query += " AND UPPER(country) = ?"
        params.append(country.upper())
    if year:
        query += " AND year = ?"
        params.append(year)
    if medal:
        query += " AND LOWER(medal) = ?"
        params.append(medal.lower())

    conn = get_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def insert_event(data: dict) -> None:
    """Insert a new athlete event/participation row."""
    # TODO: validate required fields before calling this
    conn = get_connection()
    conn.execute(
        "INSERT INTO olympics (athlete, age, country, year, season, city, sport, event, medal) "
        "VALUES (:athlete, :age, :country, :year, :season, :city, :sport, :event, :medal)",
        data,
    )
    conn.commit()
    conn.close()


# --- User queries ---

def get_user(user_id: str) -> Optional[dict]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_email(email: str) -> Optional[dict]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_users() -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM users").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_user(user_id: str, email: str, hashed_password: str, tokens: int) -> None:
    conn = get_connection()
    conn.execute(
        "INSERT INTO users (user_id, email, password, tokens) VALUES (?, ?, ?, ?)",
        (user_id, email, hashed_password, tokens),
    )
    conn.commit()
    conn.close()


def update_user(user_id: str, fields: dict) -> None:
    """Update arbitrary user fields. fields = {"email": ..., "password": ...}"""
    # TODO: add validation so only allowed fields can be updated
    set_clause = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [user_id]
    conn = get_connection()
    conn.execute(f"UPDATE users SET {set_clause} WHERE user_id = ?", values)
    conn.commit()
    conn.close()


def delete_user(user_id: str) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def deduct_token(user_id: str) -> bool:
    """Remove 1 token from user. Returns False if user has 0 tokens."""
    conn = get_connection()
    row = conn.execute("SELECT tokens FROM users WHERE user_id = ?", (user_id,)).fetchone()
    if not row or row["tokens"] <= 0:
        conn.close()
        return False
    conn.execute("UPDATE users SET tokens = tokens - 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return True


def add_tokens(user_id: str, amount: int) -> None:
    conn = get_connection()
    conn.execute("UPDATE users SET tokens = tokens + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()
