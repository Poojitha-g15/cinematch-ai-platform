from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class RecommendationResult:
    movie_id: int
    score: float


class ContentRecommender:
    """Small content-based recommender using movie descriptions, genres, and tags."""

    def __init__(self, movies: Iterable[dict]):
        self.df = pd.DataFrame(list(movies))
        if self.df.empty:
            self.vectorizer = None
            self.matrix = None
            return
        text = (
            self.df["title"].fillna("")
            + " "
            + self.df["genre"].fillna("")
            + " "
            + self.df["description"].fillna("")
            + " "
            + self.df["tags"].fillna("")
        )
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.matrix = self.vectorizer.fit_transform(text)

    def recommend_from_movie_ids(self, liked_movie_ids: list[int], limit: int = 6) -> list[RecommendationResult]:
        if self.df.empty or self.matrix is None or not liked_movie_ids:
            return []
        liked_indices = self.df.index[self.df["id"].isin(liked_movie_ids)].tolist()
        if not liked_indices:
            return []
        profile = self.matrix[liked_indices].mean(axis=0)
        scores = cosine_similarity(profile, self.matrix).flatten()
        scored = []
        liked_set = set(liked_movie_ids)
        for index, score in enumerate(scores):
            movie_id = int(self.df.iloc[index]["id"])
            if movie_id not in liked_set:
                scored.append(RecommendationResult(movie_id=movie_id, score=round(float(score), 4)))
        return sorted(scored, key=lambda item: item.score, reverse=True)[:limit]

    def recommend_from_query(self, query: str, limit: int = 6) -> list[RecommendationResult]:
        if self.df.empty or self.matrix is None or not query.strip():
            return []
        query_vector = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self.matrix).flatten()
        scored = [
            RecommendationResult(movie_id=int(self.df.iloc[index]["id"]), score=round(float(score), 4))
            for index, score in enumerate(scores)
        ]
        return sorted(scored, key=lambda item: item.score, reverse=True)[:limit]
