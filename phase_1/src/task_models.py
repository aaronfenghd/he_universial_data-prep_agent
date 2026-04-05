"""Task input models and lightweight validation for Phase 1."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import json
from pathlib import Path


@dataclass
class TaskInput:
    """Standard Phase 1 task input."""

    parameter_question: str
    population: str = ""
    line_of_therapy: str = ""
    geography: str = ""
    preferred_study_type: str = ""
    exclusion_rules: list[str] = field(default_factory=list)
    notes: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TaskInput":
        if not data.get("parameter_question"):
            raise ValueError("'parameter_question' is required.")

        exclusion_rules = data.get("exclusion_rules", [])
        if exclusion_rules is None:
            exclusion_rules = []
        if not isinstance(exclusion_rules, list) or not all(
            isinstance(item, str) for item in exclusion_rules
        ):
            raise ValueError("'exclusion_rules' must be a list of strings.")

        return cls(
            parameter_question=str(data["parameter_question"]).strip(),
            population=str(data.get("population", "")).strip(),
            line_of_therapy=str(data.get("line_of_therapy", "")).strip(),
            geography=str(data.get("geography", "")).strip(),
            preferred_study_type=str(data.get("preferred_study_type", "")).strip(),
            exclusion_rules=exclusion_rules,
            notes=str(data.get("notes", "")).strip(),
        )

    @classmethod
    def from_json_file(cls, path: Path) -> "TaskInput":
        with path.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        return cls.from_dict(raw)

    def to_query_text(self) -> str:
        """Build a simple search query string from available fields."""
        parts = [
            self.parameter_question,
            self.population,
            self.line_of_therapy,
            self.geography,
            self.preferred_study_type,
        ]
        return " ".join(p for p in parts if p).strip()
