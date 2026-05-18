import sqlite3
import os

DB_PATH = "ost_bot.db"


def init_db():
    """Initialize the SQLite database and create tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS watchlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            drama_name TEXT NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, drama_name)
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized")


def add_to_watchlist(user_id: str, drama_name: str) -> bool:
    """Add a drama to a user's watchlist. Returns False if already exists."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO watchlist (user_id, drama_name) VALUES (?, ?)",
            (user_id, drama_name)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Already in watchlist
    finally:
        conn.close()


def get_watchlist(user_id: str) -> list:
    """Get all dramas in a user's watchlist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT drama_name, added_at FROM watchlist WHERE user_id = ? ORDER BY added_at DESC",
        (user_id,)
    )
    results = cursor.fetchall()
    conn.close()
    return results


def remove_from_watchlist(user_id: str, drama_name: str) -> bool:
    """Remove a drama from a user's watchlist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM watchlist WHERE user_id = ? AND drama_name = ?",
        (user_id, drama_name)
    )
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0
