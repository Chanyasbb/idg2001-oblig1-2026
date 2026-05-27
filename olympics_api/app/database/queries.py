"""Reusable DB query helpers — keeps route handlers clean."""

from typing import Optional
from app.database.connections import get_connection


def _sport_name(slug: str) -> str:
    """Normalize a URL slug to a sport name for DB matching.

    e.g. 'ski-jumping' → 'ski jumping' (LOWER comparison handles title case)
    """
    return slug.replace("-", " ").lower()


def get_athlete(athlete_id: int) -> Optional[dict]:
    """Fetch the olympics row with the given auto-increment ID."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM olympics WHERE id = ?", (athlete_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_athlete_by_name(name: str) -> list[dict]:
    """Fetch all records where the athlete name contains `name` (case-insensitive)."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM olympics WHERE LOWER(athlete) LIKE ?",
        (f"%{name.lower()}%",),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_country(noc_code: str) -> list[dict]:
    """Fetch all records for a country by its NOC code (e.g. 'NOR')."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM olympics WHERE UPPER(noc) = ?", (noc_code.upper(),)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_sport(
    sport_slug: str,
    country: Optional[str] = None,
    year: Optional[int] = None,
    medal: Optional[str] = None,
) -> list[dict]:
    """Fetch sport records with optional filters.

    sport_slug accepts URL-style slugs ('ski-jumping') or plain names ('skiing').
    country is a NOC code; medal is 'gold', 'silver', or 'bronze'.
    """
    query = "SELECT * FROM olympics WHERE LOWER(sport) = ?"
    params: list = [_sport_name(sport_slug)]

    if country:
        query += " AND UPPER(noc) = ?"
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
    """Insert a new athlete participation row."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO olympics "
        "(athlete, sex, age, height, weight, team, noc, games, "
        "year, season, city, sport, event, medal) "
        "VALUES (:athlete, :sex, :age, :height, :weight, :team, :noc, :games, "
        ":year, :season, :city, :sport, :event, :medal)",
        data,
    )
    conn.commit()
    conn.close()


def get_user(user_id: str) -> Optional[dict]:
    """Fetch a user by user_id."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE user_id = ?", (user_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_email(email: str) -> Optional[dict]:
    """Fetch a user by email address."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE email = ?", (email,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_users() -> list[dict]:
    """Fetch all users."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM users").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_user(user_id: str, email: str, hashed_password: str, tokens: int) -> None:
    """Insert a new user row."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO users (user_id, email, password, tokens) VALUES (?, ?, ?, ?)",
        (user_id, email, hashed_password, tokens),
    )
    conn.commit()
    conn.close()


_ALLOWED_USER_FIELDS = {"email", "password"}


def update_user(user_id: str, fields: dict) -> None:
    """Update allowed user fields (email and/or password).

    Uses an allowlist to prevent column injection via arbitrary field names.
    """
    safe = {k: v for k, v in fields.items() if k in _ALLOWED_USER_FIELDS}
    if not safe:
        return
    set_clause = ", ".join(f"{k} = ?" for k in safe)
    values = list(safe.values()) + [user_id]
    conn = get_connection()
    conn.execute(f"UPDATE users SET {set_clause} WHERE user_id = ?", values)
    conn.commit()
    conn.close()


def delete_user(user_id: str) -> None:
    """Delete a user by user_id."""
    conn = get_connection()
    conn.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def deduct_tokens(user_id: str, amount: int = 1) -> bool:
    """Deduct `amount` tokens from user. Returns False if balance is too low."""
    conn = get_connection()
    row = conn.execute(
        "SELECT tokens FROM users WHERE user_id = ?", (user_id,)
    ).fetchone()
    if not row or row["tokens"] < amount:
        conn.close()
        return False
    conn.execute(
        "UPDATE users SET tokens = tokens - ? WHERE user_id = ?", (amount, user_id)
    )
    conn.commit()
    conn.close()
    return True


def add_tokens(user_id: str, amount: int) -> None:
    """Add `amount` tokens to a user's balance."""
    conn = get_connection()
    conn.execute(
        "UPDATE users SET tokens = tokens + ? WHERE user_id = ?", (amount, user_id)
    )
    conn.commit()
    conn.close()
