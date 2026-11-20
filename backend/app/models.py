"""Public request and response contracts for the SpeakQuest API."""
from pydantic import BaseModel, Field, field_validator


class QuestionOut(BaseModel):
    id: str
    text: str
    translation: str


class LessonOut(BaseModel):
    id: str
    title: str
    subtitle: str
    icon: str
    questions: list[QuestionOut]


class EvaluateIn(BaseModel):
    lesson_id: str = Field(min_length=1, max_length=40)
    question_id: str = Field(min_length=1, max_length=40)
    transcript: str = Field(min_length=1, max_length=400)

    @field_validator("transcript")
    @classmethod
    def nonempty_transcript(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("transcript cannot be blank")
        return value


class ProgressOut(BaseModel):
    xp: int
    streak: int
    completed_question_ids: list[str]


class SessionOut(BaseModel):
    session_token: str
    progress: ProgressOut


class EvaluateOut(BaseModel):
    score: int = Field(ge=0, le=100)
    passed: bool
    expected_text: str
    transcript: str
    matched_words: list[str]
    missing_words: list[str]
    feedback: str
    xp_gained: int = 0
    progress: ProgressOut | None = None
