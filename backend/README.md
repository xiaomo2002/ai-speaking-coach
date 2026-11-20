# SpeakQuest FastAPI backend

This is a working REST API for the existing SpeakQuest English speaking challenge game. It ships 15 sentences across 3 lessons, deterministic word-order-aware scoring, anonymous session creation, and SQLite-backed XP/progress.

**It does not implement LLM conversation, acoustic pronunciation grading, or user accounts.** The current frontend can still work offline using its own local scoring; the backend is independently accessible and also serves the frontend at `/`.

## Quick start

Requires Python 3.10 or newer.

```bash
cd backend
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Visit http://127.0.0.1:8000/docs for interactive OpenAPI documentation, or http://127.0.0.1:8000/ to load the existing browser game.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Liveness check |
| GET | `/api/v1/lessons` | List the 3 lessons (15 questions) |
| GET | `/api/v1/lessons/{lesson_id}` | Return a lesson |
| POST | `/api/v1/practice/evaluate` | Compare recognized/typed text against a target sentence |
| POST | `/api/v1/sessions` | Create a random practice-session token |
| GET | `/api/v1/progress` | Fetch saved XP/streak/completions (Bearer token required) |

### Sample flow

```bash
# 1. Create a session. Save session_token from the JSON response.
curl -X POST http://127.0.0.1:8000/api/v1/sessions

# 2. Practice a sentence; replace TOKEN with your session token.
curl -X POST http://127.0.0.1:8000/api/v1/practice/evaluate \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer TOKEN' \
  -d '{"lesson_id":"daily","question_id":"daily-1","transcript":"Hello nice to meet you"}'

# 3. Read persisted progress.
curl http://127.0.0.1:8000/api/v1/progress -H 'Authorization: Bearer TOKEN'
```

The `Authorization` header is **optional for evaluation**: without it, you still receive a score but no XP is saved. Score is case/punctuation-insensitive word-order similarity with an 80% pass threshold; **not pronunciation scoring**. New completed questions earn 20 XP; repeating a finished question does not earn additional XP.

## Configuration

| Environment variable | Default | Meaning |
| --- | --- | --- |
| `SPEAKQUEST_DB_PATH` | `backend/.data/speakquest.sqlite3` | SQLite DB location |
| `SPEAKQUEST_CORS_ORIGINS` | unset | Comma-separated explicit browser origins allowed to call this API |

Do not commit the `.data` directory. Treat `session_token` as a secret, because it grants access to that session's progress. Add authentication, rate limiting, backups and production configuration before hosting a public multi-user service.

## Tests

```bash
cd backend
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

GitHub Actions runs the backend tests on relevant pushes and pull requests.
