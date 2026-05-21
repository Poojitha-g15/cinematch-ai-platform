# API Examples

Start the server:

```bash
uvicorn src.app:app --reload
```

## Health check

```bash
curl http://127.0.0.1:8000/health
```

## Register

```bash
curl -X POST http://127.0.0.1:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Poojitha","email":"poojitha@example.com","password":"Password123"}'
```

## Login

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"poojitha@example.com","password":"Password123"}'
```

Copy the token from the response.

## Save a movie to watchlist

```bash
curl -X POST http://127.0.0.1:8000/api/watchlist/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Rate a movie

```bash
curl -X POST http://127.0.0.1:8000/api/ratings/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"rating":5}'
```

## Personalized recommendations

```bash
curl http://127.0.0.1:8000/api/recommendations \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Query-based recommendations

```bash
curl -X POST http://127.0.0.1:8000/api/recommendations/query \
  -H "Content-Type: application/json" \
  -d '{"query":"AI cybersecurity software systems"}'
```
