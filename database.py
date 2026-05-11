"""
database.py – SQLite case history storage for DharmaSetu.
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "cases.db"


def _connect() -> sqlite3.Connection:
    """Return a connection with row_factory for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the cases table if it does not exist."""
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cases (
                case_id   INTEGER PRIMARY KEY AUTOINCREMENT,
                user_query TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                role      TEXT NOT NULL,
                language  TEXT NOT NULL DEFAULT 'English',
                timestamp TEXT NOT NULL
            )
        """)


def save_case(user_query: str, ai_response: str, role: str, language: str) -> int:
    """Save a case to the database and return the new case_id."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with _connect() as conn:
        cursor = conn.execute(
            "INSERT INTO cases (user_query, ai_response, role, language, timestamp) VALUES (?, ?, ?, ?, ?)",
            (user_query, ai_response, role, language, timestamp),
        )
        return cursor.lastrowid


def get_all_cases() -> list:
    """Return all cases ordered by most recent first."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT case_id, user_query, role, language, timestamp FROM cases ORDER BY case_id DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def get_case_by_id(case_id: int):
    """Return a single case by ID, or None if not found."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM cases WHERE case_id = ?", (case_id,)
        ).fetchone()
        return dict(row) if row else None
