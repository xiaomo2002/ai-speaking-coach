"""SpeakQuest API.

Run from the backend directory:
    uvicorn app.main:app --reload
"""
from contextlib import asynccontextmanager
from pathlib import Path
import os

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .data import LESSONS, LESSONS_BY_ID
from .models import EvaluateIn, EvaluateOut, LessonOut, ProgressOut, SessionOut
from .scoring import evaluate_text
from .store import ProgressStore


REPO_ROOT = Path(__file__).resolve().parents[2]


def create_app(database_path: str | Path | None = None) -> FastAPI:
    db_path = database_path or os.getenv(
        "SPEAKQUEST_DB_PATH", str(Path(__file__).resolve().parents[1] / ".data" / "speakquest.sqlite3")
    )

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        store = ProgressStore(db_path)
        store.initialize()
        application.state.store = store
        yield

    api = FastAPI(
        title="SpeakQuest Speaking Practice API",
        description="Lessons, word-order-aware text assessment and anonymous progress. Not a pronunciation or AI model.",
        version="0.1.0",
        lifespan=lifespan,
    )

    allowed_origins = [
        item.strip() for item in os.getenv("SPEAKQUEST_CORS_ORIGINS", "").split(",")
        if item.strip()
    ]
    if allowed_origins:
        api.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_methods=["GET", "POST"],
            allow_headers=["Authorization", "Content-Type"],
        )

    @api.get("/", include_in_schema=False)
    def home():
        return FileResponse(REPO_ROOT / "index.html")

    @api.get("/health", tags=["System"])
    def health():
        return {"status": "ok", "service": "speakquest-api", "version": "0.1.0"}

    @api.get("/api/v1/lessons", response_model=list[LessonOut], tags=["Lessons"])
    def list_lessons():
        return LESSONS

    @api.get("/api/v1/lessons/{lesson_id}", response_model=LessonOut, tags=["Lessons"])
    def get_lesson(lesson_id: str):
        lesson = LESSONS_BY_ID.get(lesson_id)
        if lesson is None:
            raise HTTPException(status_code=404, detail="Lesson not found")
        return lesson

    @api.post("/api/v1/sessions", response_model=SessionOut, status_code=201, tags=["Progress"])
    def start_session(request: Request):
        store: ProgressStore = request.app.state.store
        token = store.create_session()
        progress = store.get_progress(token)
        assert progress is not None
        return SessionOut(session_token=token, progress=progress)

    @api.get("/api/v1/progress", response_model=ProgressOut, tags=["Progress"])
    def get_progress(request: Request, authorization: str | None = Header(default=None)):
        token = parse_bearer(authorization)
        store: ProgressStore = request.app.state.store
        progress = store.get_progress(token)
        if progress is None:
            raise HTTPException(status_code=401, detail="Invalid session token")
        return progress

    @api.post("/api/v1/practice/evaluate", response_model=EvaluateOut, tags=["Practice"])
    def evaluate(
        body: EvaluateIn,
        request: Request,
        authorization: str | None = Header(default=None),
    ):
        lesson = LESSONS_BY_ID.get(body.lesson_id)
        if lesson is None:
            raise HTTPException(status_code=404, detail="Lesson not found")
        question = next((q for q in lesson.questions if q.id == body.question_id), None)
        if question is None:
            raise HTTPException(status_code=404, detail="Question not found in this lesson")

        result = evaluate_text(question.text, body.transcript)
        xp_gained = 0
        progress = None
        if authorization is not None:
            token = parse_bearer(authorization)
            store: ProgressStore = request.app.state.store
            outcome = store.record_result(token, question.id, result["passed"])
            if outcome is None:
                raise HTTPException(status_code=401, detail="Invalid session token")
            progress, xp_gained = outcome
        return EvaluateOut(
            expected_text=question.text,
            transcript=body.transcript,
            xp_gained=xp_gained,
            progress=progress,
            **result,
        )

    return api


def parse_bearer(value: str | None) -> str:
    if not value or not value.startswith("Bearer ") or not value[7:].strip():
        raise HTTPException(status_code=401, detail="Bearer session token required")
    return value[7:].strip()


app = create_app()
