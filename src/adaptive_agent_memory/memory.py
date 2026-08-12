from __future__ import annotations

import json
import math
import re
import sqlite3
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .models import Experience, MemoryMatch

_TOKEN_RE = re.compile(r"[a-zA-Z0-9_äöüÄÖÜß]+")


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in _TOKEN_RE.findall(text) if len(t) > 1}


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


class AdaptiveMemory:
    def __init__(self, path: str | Path = "agent_memory.db") -> None:
        self.path = str(path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS experiences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    context TEXT NOT NULL,
                    action TEXT NOT NULL,
                    expected_outcome TEXT NOT NULL,
                    actual_outcome TEXT NOT NULL,
                    success REAL NOT NULL,
                    prediction_error REAL NOT NULL,
                    state_before REAL,
                    state_after REAL,
                    tags_json TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_experiences_created_at ON experiences(created_at)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_experiences_action ON experiences(action)"
            )

    def record(self, experience: Experience) -> int:
        experience.validate()
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO experiences (
                    context, action, expected_outcome, actual_outcome,
                    success, prediction_error, state_before, state_after,
                    tags_json, metadata_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    experience.context,
                    experience.action,
                    experience.expected_outcome,
                    experience.actual_outcome,
                    experience.success,
                    experience.prediction_error,
                    experience.state_before,
                    experience.state_after,
                    json.dumps(experience.tags, ensure_ascii=False),
                    json.dumps(experience.metadata, ensure_ascii=False),
                    experience.created_at,
                ),
            )
            return int(cur.lastrowid)

    def _row_to_experience(self, row: sqlite3.Row) -> Experience:
        return Experience(
            context=row["context"],
            action=row["action"],
            expected_outcome=row["expected_outcome"],
            actual_outcome=row["actual_outcome"],
            success=float(row["success"]),
            prediction_error=float(row["prediction_error"]),
            state_before=row["state_before"],
            state_after=row["state_after"],
            tags=json.loads(row["tags_json"]),
            metadata=json.loads(row["metadata_json"]),
            created_at=row["created_at"],
        )

    def recall(self, query: str, limit: int = 5) -> list[MemoryMatch]:
        if limit <= 0:
            return []

        query_tokens = _tokens(query)
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM experiences ORDER BY id DESC LIMIT 500"
            ).fetchall()

        now = datetime.now(timezone.utc)
        matches: list[MemoryMatch] = []
        for row in rows:
            exp = self._row_to_experience(row)
            searchable = " ".join(
                [exp.context, exp.action, exp.expected_outcome, exp.actual_outcome, " ".join(exp.tags)]
            )
            relevance = _jaccard(query_tokens, _tokens(searchable))

            try:
                created = datetime.fromisoformat(exp.created_at)
                if created.tzinfo is None:
                    created = created.replace(tzinfo=timezone.utc)
                age_days = max(0.0, (now - created).total_seconds() / 86400)
            except ValueError:
                age_days = 365.0

            recency = math.exp(-age_days / 90.0)
            quality = max(0.0, min(1.0, exp.success * (1.0 / (1.0 + exp.prediction_error))))
            score = 0.60 * relevance + 0.25 * quality + 0.15 * recency

            if relevance > 0 or exp.action.lower() in query.lower():
                matches.append(MemoryMatch(exp, relevance, score))

        matches.sort(key=lambda m: m.score, reverse=True)
        return matches[:limit]

    def advise(self, query: str, limit: int = 3) -> str:
        matches = self.recall(query, limit=limit)
        if not matches:
            return "No relevant prior experience found."

        lines = ["Relevant prior experience:"]
        for index, match in enumerate(matches, 1):
            exp = match.experience
            verdict = "worked well" if exp.success >= 0.75 else "was mixed" if exp.success >= 0.4 else "often failed"
            lines.append(
                f"{index}. Action '{exp.action}' {verdict} (success={exp.success:.2f}, score={match.score:.2f}). "
                f"Outcome: {exp.actual_outcome}"
            )
        return "\n".join(lines)

    def stats(self) -> dict[str, float | int]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS n, AVG(success) AS avg_success, AVG(prediction_error) AS avg_error FROM experiences"
            ).fetchone()
        return {
            "count": int(row["n"] or 0),
            "average_success": float(row["avg_success"] or 0.0),
            "average_prediction_error": float(row["avg_error"] or 0.0),
        }

    def export_json(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM experiences ORDER BY id ASC").fetchall()
        return [asdict(self._row_to_experience(row)) for row in rows]
