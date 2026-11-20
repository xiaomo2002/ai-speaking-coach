"""Small SQLite persistence layer for anonymous practice sessions.

A cryptographically random bearer token identifies a single demo session.
Do not use this as a replacement for real accounts/authentication.
"""
from contextlib import closing
from pathlib import Path
import secrets
import sqlite3

from .models import ProgressOut


class ProgressStore:
    def __init__(self, database_path: str | Path):
        self.database_path = Path(database_path)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=10)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self._connect()) as conn, conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    token TEXT PRIMARY KEY,
                    xp INTEGER NOT NULL DEFAULT 0,
                    streak INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS completions (
                    token TEXT NOT NULL REFERENCES sessions(token) ON DELETE CASCADE,
                    question_id TEXT NOT NULL,
                    PRIMARY KEY (token, question_id)
                );
                """
            )

    def create_session(self) -> str:
        token = secrets.token_urlsafe(32)
        with closing(self._connect()) as conn, conn:
            conn.execute("INSERT INTO sessions (token) VALUES (?)", (token,))
        return token

    def get_progress(self, token: str) -> ProgressOut | None:
        with closing(self._connect()) as conn:
            row = conn.execute(
                "SELECT xp, streak FROM sessions WHERE token = ?", (token,)
            ).fetchone()
            if row is None:
                return None
            question_ids = [
                item[0] for item in conn.execute(
                    "SELECT question_id FROM completions WHERE token = ? ORDER BY question_id",
                    (token,),
                ).fetchall()
            ]
        return ProgressOut(
            xp=row[0], streak=row[1], completed_question_ids=question_ids
        )

    def record_result(self, token: str, question_id: str, passed: bool) -> tuple[ProgressOut, int] | None:
        """Award 20 XP only once per question; failed attempts reset streak."""
        xp_gained = 0
        with closing(self._connect()) as conn, conn:
            session = conn.execute(
                "SELECT token FROM sessions WHERE token = ?", (token,)
            ).fetchone()
            if session is None:
                return None
            already_done = conn.execute(
                "SELECT 1 FROM completions WHERE token = ? AND question_id = ?",
                (token, question_id),
            ).fetchone()
            if passed and not already_done:
                conn.execute(
                    "INSERT INTO completions (token, question_id) VALUES (?, ?)",
                    (token, question_id),
                )
                conn.execute(
                    "UPDATE sessions SET xp = xp + 20, streak = streak + 1 WHERE token = ?",
                    (token,),
                )
                xp_gained = 20
            elif not passed:
                conn.execute("UPDATE sessions SET streak = 0 WHERE token = ?", (token,))
        progress = self.get_progress(token)
        assert progress is not None
        return progress, xp_gained
