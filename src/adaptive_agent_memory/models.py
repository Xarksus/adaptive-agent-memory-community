from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class Experience:
    context: str
    action: str
    expected_outcome: str
    actual_outcome: str
    success: float
    prediction_error: float = 0.0
    state_before: float | None = None
    state_after: float | None = None
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def validate(self) -> None:
        if not 0.0 <= self.success <= 1.0:
            raise ValueError("success must be between 0.0 and 1.0")
        if self.prediction_error < 0.0:
            raise ValueError("prediction_error must be non-negative")
        if not self.context.strip():
            raise ValueError("context must not be empty")
        if not self.action.strip():
            raise ValueError("action must not be empty")


@dataclass(slots=True)
class MemoryMatch:
    experience: Experience
    relevance: float
    score: float
