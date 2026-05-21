# Project Explanation

## What this project does

CineMatch AI Platform is a full-stack movie discovery app. Users can register, log in, browse movies, save a watchlist, rate movies, and receive recommendations.

## What problem it solves

Streaming platforms need to personalize content while managing users, preferences, ratings, and analytics. This project demonstrates a smaller version of that real-world workflow.

## Main modules

### Authentication

The app stores users in SQLite, hashes passwords using PBKDF2, and issues signed tokens for protected API routes.

### Movie discovery

Users can search across movie titles, descriptions, and tags. They can also filter by genre.

### Watchlist and ratings

Logged-in users can save movies and rate them. This creates user preference data.

### Recommendations

The recommender uses TF-IDF to vectorize movie title, genre, description, and tags. It calculates cosine similarity to recommend movies similar to a user's watchlist or query.

### Analytics

The app exposes simple analytics such as movie count, registered users, watchlist saves, top genres, and top-rated movies.

## Why this is good for software engineering roles

This project shows more than UI. It shows backend routing, API design, database operations, authentication, data processing, ML-style recommendation logic, testing, and Docker readiness.
