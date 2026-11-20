# SpeakQuest · AI Speaking Coach

A friendly English-speaking practice game with a real FastAPI backend. The browser game already works without a backend; the new API adds lesson endpoints, text-based evaluation and persisted anonymous session progress.

> Current scope: **speaking practice MVP**, not live AI conversations or acoustic pronunciation assessment.

## What's included

- **Frontend (`index.html`)**: responsive speaking game, three lessons, example voice playback and browser speech recognition (or typed text), local XP and progress.
- **FastAPI (`backend/app/`)**: structured lessons, versioned REST endpoints, word-order-aware evaluation, token-based practice sessions and SQLite progress.
- **Tests (`backend/tests/`)** and a GitHub Actions CI workflow.

## Start the web app + API

```bash
cd backend
python -m venv .venv
# Activate the virtual environment for your shell
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

- Game: http://127.0.0.1:8000/
- Interactive API docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

See [backend/README.md](backend/README.md) for API examples, persistence, environment variables, tests and security notes.

## Frontend-only mode

Open `index.html` directly, or deploy the repository's root directory through GitHub Pages. This mode does **not** require Python, accounts, or paid API keys; scores and progress are stored in the local browser.

Speech recognition depends on browser support and may involve the browser vendor's online speech service. In both frontend and backend, scoring compares words with an example sentence; it is not a professional pronunciation test.

## License

MIT License (see [LICENSE](LICENSE)).
