import csv
import os
import sqlite3
from pathlib import Path
from typing import Iterable

BASE_DIR = Path(__file__).resolve().parents[1]
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", BASE_DIR / "cinematch.db"))
MOVIE_DATA_PATH = BASE_DIR / "data" / "movies.csv"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            genre TEXT NOT NULL,
            year INTEGER NOT NULL,
            runtime INTEGER NOT NULL,
            description TEXT NOT NULL,
            tags TEXT NOT NULL,
            vote_average REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS watchlist (
            user_id INTEGER NOT NULL,
            movie_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'watchlist',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, movie_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (movie_id) REFERENCES movies(id)
        );

        CREATE TABLE IF NOT EXISTS ratings (
            user_id INTEGER NOT NULL,
            movie_id INTEGER NOT NULL,
            rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, movie_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (movie_id) REFERENCES movies(id)
        );
        """
    )
    conn.commit()
    seed_movies(conn)
    conn.close()


def seed_movies(conn: sqlite3.Connection) -> None:
    count = conn.execute("SELECT COUNT(*) AS count FROM movies").fetchone()["count"]
    if count:
        return
    with MOVIE_DATA_PATH.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = [
            (
                int(row["id"]),
                row["title"],
                row["genre"],
                int(row["year"]),
                int(row["runtime"]),
                row["description"],
                row["tags"],
                float(row["vote_average"]),
            )
            for row in reader
        ]
    conn.executemany(
        """
        INSERT INTO movies (id, title, genre, year, runtime, description, tags, vote_average)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    conn.commit()


def rows_to_dicts(rows: Iterable[sqlite3.Row]) -> list[dict]:
    return [dict(row) for row in rows]
