# CineMatch AI Platform

A full-stack Python movie platform with user authentication, movie discovery, watchlists, ratings, analytics, and AI-style content-based recommendations.

This project is an upgraded replacement for a basic user-authentication movie app. It is designed to look stronger on a software engineering, backend, Python, full-stack, or data-focused resume.

## Why this project is useful

Many beginner movie projects only show UI screens. This version shows real application engineering:

- User registration and login
- Password hashing with PBKDF2
- Token-based protected routes
- SQLite database tables
- REST API design with FastAPI
- Movie search and genre filtering
- Watchlist and rating workflows
- Content-based recommendations using TF-IDF and cosine similarity
- Dashboard analytics
- Static frontend using HTML, CSS, and JavaScript
- Pytest tests
- Docker support
- GitHub Actions workflow

## Tech stack

| Area | Tools |
|---|---|
| Backend | Python, FastAPI |
| Database | SQLite |
| ML / Data | pandas, scikit-learn, TF-IDF, cosine similarity |
| Frontend | HTML, CSS, JavaScript |
| Testing | pytest, FastAPI TestClient |
| DevOps | Docker, GitHub Actions |

## Project structure

```text
cinematch-ai-platform/
├── data/
│   └── movies.csv
├── docs/
│   ├── API_EXAMPLES.md
│   ├── GITHUB_PUSH_STEPS.md
│   ├── PROJECT_EXPLANATION.md
│   └── RESUME_POINTS.md
├── src/
│   ├── app.py
│   ├── database.py
│   ├── recommender.py
│   ├── schemas.py
│   └── security.py
├── static/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── tests/
│   └── test_app.py
├── .github/workflows/ci.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## How to run locally

### 1. Open the project in VS Code

Open the folder named:

```bash
cinematch-ai-platform
```

Then open a terminal in VS Code.

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
uvicorn src.app:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```

## How to use the app

1. Create a user account.
2. Search movies by title, description, tag, or genre.
3. Save movies to your watchlist.
4. Rate movies.
5. Load recommendations based on your saved and highly rated movies.
6. Try query-based recommendations by entering a phrase like:

```text
AI cybersecurity data systems
```

## Example API flow

Register:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Poojitha","email":"poojitha@example.com","password":"Password123"}'
```

Login:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"poojitha@example.com","password":"Password123"}'
```

List movies:

```bash
curl http://127.0.0.1:8000/api/movies
```

## Run tests

```bash
pytest
```

## Run with Docker

```bash
docker build -t cinematch-ai-platform .
docker run -p 8000:8000 cinematch-ai-platform
```

Open:

```text
http://127.0.0.1:8000
```

## Recommended GitHub repo name

```text
cinematch-ai-platform
```

## Resume title

```text
CineMatch AI Platform: Full-Stack Movie Recommendation and Authentication System
```

## Resume bullet

```text
Built a full-stack Python movie platform with FastAPI, SQLite, token-based authentication, watchlist/rating workflows, and content-based recommendations using TF-IDF and cosine similarity.
```

## Future improvements

- Replace sample CSV with TMDB API integration
- Add PostgreSQL support
- Add admin movie management
- Add refresh tokens
- Add role-based access control
- Deploy backend on Render or Railway
- Deploy frontend separately on Vercel
