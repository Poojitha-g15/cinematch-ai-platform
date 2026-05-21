from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .database import get_connection, init_db, rows_to_dicts
from .recommender import ContentRecommender
from .schemas import LoginRequest, RatingRequest, RecommendationQuery, RegisterRequest
from .security import create_token, decode_token, hash_password, verify_password

BASE_DIR = Path(__file__).resolve().parents[1]
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="CineMatch AI Platform",
    description="Full-stack movie platform with authentication, watchlists, ratings, analytics, and content-based recommendations.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "cinematch-ai-platform"}


def get_current_user(authorization: Optional[str] = Header(default=None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authentication token")
    token = authorization.replace("Bearer ", "", 1)
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    conn = get_connection()
    user = conn.execute("SELECT id, name, email FROM users WHERE id = ?", (payload["sub"],)).fetchone()
    conn.close()
    if user is None:
        raise HTTPException(status_code=401, detail="User no longer exists")
    return dict(user)


@app.post("/api/auth/register")
def register(request: RegisterRequest) -> dict:
    conn = get_connection()
    existing = conn.execute("SELECT id FROM users WHERE email = ?", (request.email.lower(),)).fetchone()
    if existing:
        conn.close()
        raise HTTPException(status_code=409, detail="Email is already registered")
    password_hash = hash_password(request.password)
    cur = conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        (request.name.strip(), request.email.lower(), password_hash),
    )
    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    return {"token": create_token(user_id, request.email.lower()), "user": {"id": user_id, "name": request.name, "email": request.email.lower()}}


@app.post("/api/auth/login")
def login(request: LoginRequest) -> dict:
    conn = get_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (request.email.lower(),)).fetchone()
    conn.close()
    if user is None or not verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"token": create_token(user["id"], user["email"]), "user": {"id": user["id"], "name": user["name"], "email": user["email"]}}


@app.get("/api/me")
def me(user: dict = Depends(get_current_user)) -> dict:
    return user


@app.get("/api/movies")
def list_movies(
    search: str = "",
    genre: str = "",
    min_year: Optional[int] = Query(default=None, ge=1900),
    max_year: Optional[int] = Query(default=None, le=2100),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[dict]:
    query = "SELECT * FROM movies WHERE 1 = 1"
    params: list = []
    if search.strip():
        term = f"%{search.lower()}%"
        query += " AND (LOWER(title) LIKE ? OR LOWER(description) LIKE ? OR LOWER(tags) LIKE ?)"
        params.extend([term, term, term])
    if genre.strip():
        query += " AND LOWER(genre) = ?"
        params.append(genre.lower())
    if min_year is not None:
        query += " AND year >= ?"
        params.append(min_year)
    if max_year is not None:
        query += " AND year <= ?"
        params.append(max_year)
    query += " ORDER BY vote_average DESC, year DESC LIMIT ?"
    params.append(limit)
    conn = get_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows_to_dicts(rows)


@app.get("/api/genres")
def genres() -> list[str]:
    conn = get_connection()
    rows = conn.execute("SELECT DISTINCT genre FROM movies ORDER BY genre").fetchall()
    conn.close()
    return [row["genre"] for row in rows]


@app.get("/api/movies/{movie_id}")
def get_movie(movie_id: int) -> dict:
    conn = get_connection()
    movie = conn.execute("SELECT * FROM movies WHERE id = ?", (movie_id,)).fetchone()
    conn.close()
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return dict(movie)


@app.post("/api/watchlist/{movie_id}")
def add_to_watchlist(movie_id: int, user: dict = Depends(get_current_user)) -> dict:
    conn = get_connection()
    movie = conn.execute("SELECT id FROM movies WHERE id = ?", (movie_id,)).fetchone()
    if movie is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Movie not found")
    conn.execute(
        "INSERT OR REPLACE INTO watchlist (user_id, movie_id, status) VALUES (?, ?, 'watchlist')",
        (user["id"], movie_id),
    )
    conn.commit()
    conn.close()
    return {"message": "Movie added to watchlist", "movie_id": movie_id}


@app.get("/api/watchlist")
def get_watchlist(user: dict = Depends(get_current_user)) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT movies.*, watchlist.created_at AS saved_at
        FROM watchlist
        JOIN movies ON movies.id = watchlist.movie_id
        WHERE watchlist.user_id = ?
        ORDER BY watchlist.created_at DESC
        """,
        (user["id"],),
    ).fetchall()
    conn.close()
    return rows_to_dicts(rows)


@app.delete("/api/watchlist/{movie_id}")
def remove_from_watchlist(movie_id: int, user: dict = Depends(get_current_user)) -> dict:
    conn = get_connection()
    conn.execute("DELETE FROM watchlist WHERE user_id = ? AND movie_id = ?", (user["id"], movie_id))
    conn.commit()
    conn.close()
    return {"message": "Movie removed from watchlist", "movie_id": movie_id}


@app.post("/api/ratings/{movie_id}")
def rate_movie(movie_id: int, request: RatingRequest, user: dict = Depends(get_current_user)) -> dict:
    conn = get_connection()
    movie = conn.execute("SELECT id FROM movies WHERE id = ?", (movie_id,)).fetchone()
    if movie is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Movie not found")
    conn.execute(
        "INSERT OR REPLACE INTO ratings (user_id, movie_id, rating) VALUES (?, ?, ?)",
        (user["id"], movie_id, request.rating),
    )
    conn.commit()
    conn.close()
    return {"message": "Rating saved", "movie_id": movie_id, "rating": request.rating}


@app.post("/api/recommendations/query")
def recommendations_from_query(request: RecommendationQuery, limit: int = Query(default=6, ge=1, le=20)) -> list[dict]:
    conn = get_connection()
    movies = rows_to_dicts(conn.execute("SELECT * FROM movies").fetchall())
    recommender = ContentRecommender(movies)
    results = recommender.recommend_from_query(request.query, limit)
    if not results:
        conn.close()
        return []
    placeholders = ",".join("?" for _ in results)
    score_by_id = {item.movie_id: item.score for item in results}
    rows = conn.execute(f"SELECT * FROM movies WHERE id IN ({placeholders})", [item.movie_id for item in results]).fetchall()
    conn.close()
    movies_by_id = {row["id"]: dict(row) for row in rows}
    return [{**movies_by_id[item.movie_id], "recommendation_score": item.score} for item in results if item.movie_id in movies_by_id]


@app.get("/api/recommendations")
def recommendations(user: dict = Depends(get_current_user), limit: int = Query(default=6, ge=1, le=20)) -> list[dict]:
    conn = get_connection()
    liked_rows = conn.execute(
        """
        SELECT movie_id FROM watchlist WHERE user_id = ?
        UNION
        SELECT movie_id FROM ratings WHERE user_id = ? AND rating >= 4
        """,
        (user["id"], user["id"]),
    ).fetchall()
    liked_ids = [row["movie_id"] for row in liked_rows]
    all_movies = rows_to_dicts(conn.execute("SELECT * FROM movies").fetchall())
    if liked_ids:
        recommender = ContentRecommender(all_movies)
        results = recommender.recommend_from_movie_ids(liked_ids, limit)
        score_by_id = {item.movie_id: item.score for item in results}
        ordered_ids = [item.movie_id for item in results]
        if ordered_ids:
            placeholders = ",".join("?" for _ in ordered_ids)
            rows = conn.execute(f"SELECT * FROM movies WHERE id IN ({placeholders})", ordered_ids).fetchall()
            movies_by_id = {row["id"]: dict(row) for row in rows}
            conn.close()
            return [{**movies_by_id[movie_id], "recommendation_score": score_by_id[movie_id]} for movie_id in ordered_ids if movie_id in movies_by_id]
    rows = conn.execute("SELECT *, vote_average AS recommendation_score FROM movies ORDER BY vote_average DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return rows_to_dicts(rows)


@app.get("/api/analytics")
def analytics() -> dict:
    conn = get_connection()
    total_movies = conn.execute("SELECT COUNT(*) AS value FROM movies").fetchone()["value"]
    total_users = conn.execute("SELECT COUNT(*) AS value FROM users").fetchone()["value"]
    total_watchlist = conn.execute("SELECT COUNT(*) AS value FROM watchlist").fetchone()["value"]
    top_genres = rows_to_dicts(conn.execute("SELECT genre, COUNT(*) AS count FROM movies GROUP BY genre ORDER BY count DESC").fetchall())
    top_movies = rows_to_dicts(conn.execute("SELECT title, vote_average FROM movies ORDER BY vote_average DESC LIMIT 5").fetchall())
    conn.close()
    return {
        "total_movies": total_movies,
        "total_users": total_users,
        "total_watchlist_items": total_watchlist,
        "top_genres": top_genres,
        "top_movies": top_movies,
    }
