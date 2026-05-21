const state = {
  token: localStorage.getItem("cinematch_token") || "",
  user: JSON.parse(localStorage.getItem("cinematch_user") || "null"),
};

const authHeaders = () => state.token ? { Authorization: `Bearer ${state.token}` } : {};
const $ = (selector) => document.querySelector(selector);

function setAuthStatus(message) {
  $("#auth-status").textContent = message;
}

async function request(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(data?.detail || "Request failed");
  }
  return data;
}

function saveSession(payload) {
  state.token = payload.token;
  state.user = payload.user;
  localStorage.setItem("cinematch_token", payload.token);
  localStorage.setItem("cinematch_user", JSON.stringify(payload.user));
  setAuthStatus(`Logged in as ${payload.user.name}`);
}

async function loadGenres() {
  const genres = await request("/api/genres");
  const select = $("#genre-filter");
  genres.forEach((genre) => {
    const option = document.createElement("option");
    option.value = genre;
    option.textContent = genre;
    select.appendChild(option);
  });
}

function movieCard(movie) {
  return `
    <article class="movie-card">
      <h3>${movie.title}</h3>
      <p><span class="badge">${movie.genre}</span><span class="badge">${movie.year}</span><span class="badge">⭐ ${movie.vote_average}</span></p>
      <p class="muted">${movie.description}</p>
      <div class="movie-actions">
        <button onclick="addWatchlist(${movie.id})">Save</button>
        <button onclick="rateMovie(${movie.id}, 5)">Rate 5</button>
      </div>
    </article>
  `;
}

async function loadMovies() {
  const params = new URLSearchParams();
  const search = $("#search").value.trim();
  const genre = $("#genre-filter").value;
  if (search) params.set("search", search);
  if (genre) params.set("genre", genre);
  const movies = await request(`/api/movies?${params}`);
  $("#movie-grid").innerHTML = movies.map(movieCard).join("") || `<p class="muted">No movies found.</p>`;
}

async function addWatchlist(movieId) {
  if (!state.token) return alert("Please login first.");
  try {
    await request(`/api/watchlist/${movieId}`, { method: "POST", headers: authHeaders() });
    alert("Added to watchlist");
  } catch (error) {
    alert(error.message);
  }
}

async function rateMovie(movieId, rating) {
  if (!state.token) return alert("Please login first.");
  try {
    await request(`/api/ratings/${movieId}`, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({ rating }),
    });
    alert("Rating saved");
  } catch (error) {
    alert(error.message);
  }
}

function resultItem(movie) {
  const score = movie.recommendation_score !== undefined ? ` · Score ${Number(movie.recommendation_score).toFixed(2)}` : "";
  return `<div class="result-item"><strong>${movie.title}</strong><span>${movie.genre} · ${movie.year}${score}</span><p class="muted">${movie.description}</p></div>`;
}

async function loadWatchlist() {
  if (!state.token) return alert("Please login first.");
  const list = await request("/api/watchlist", { headers: authHeaders() });
  $("#watchlist").innerHTML = list.map(resultItem).join("") || `<p class="muted">Your watchlist is empty.</p>`;
}

async function loadRecommendations() {
  if (!state.token) return alert("Please login first.");
  const list = await request("/api/recommendations", { headers: authHeaders() });
  $("#recommendations-list").innerHTML = list.map(resultItem).join("") || `<p class="muted">Save movies first to improve recommendations.</p>`;
}

async function queryRecommendations() {
  const query = $("#recommendation-query").value.trim();
  if (query.length < 2) return alert("Enter a short description first.");
  const list = await request("/api/recommendations/query", {
    method: "POST",
    body: JSON.stringify({ query }),
  });
  $("#query-results").innerHTML = list.map(resultItem).join("") || `<p class="muted">No recommendations found.</p>`;
}

async function loadAnalytics() {
  const analytics = await request("/api/analytics");
  $("#analytics-output").innerHTML = `
    <div class="analytics-box"><strong>Total movies:</strong> ${analytics.total_movies}</div>
    <div class="analytics-box"><strong>Registered users:</strong> ${analytics.total_users}</div>
    <div class="analytics-box"><strong>Watchlist saves:</strong> ${analytics.total_watchlist_items}</div>
    <div class="analytics-box"><strong>Top genres:</strong> ${analytics.top_genres.map(g => `${g.genre} (${g.count})`).join(", ")}</div>
  `;
}

$("#register-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(event.target);
  try {
    const payload = await request("/api/auth/register", {
      method: "POST",
      body: JSON.stringify(Object.fromEntries(form.entries())),
    });
    saveSession(payload);
    event.target.reset();
  } catch (error) {
    setAuthStatus(error.message);
  }
});

$("#login-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(event.target);
  try {
    const payload = await request("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(Object.fromEntries(form.entries())),
    });
    saveSession(payload);
    event.target.reset();
  } catch (error) {
    setAuthStatus(error.message);
  }
});

$("#load-movies").addEventListener("click", loadMovies);
$("#load-watchlist").addEventListener("click", loadWatchlist);
$("#load-recommendations").addEventListener("click", loadRecommendations);
$("#query-recommendations").addEventListener("click", queryRecommendations);
$("#load-analytics").addEventListener("click", loadAnalytics);

if (state.user) setAuthStatus(`Logged in as ${state.user.name}`);
loadGenres();
loadMovies();
loadAnalytics();
