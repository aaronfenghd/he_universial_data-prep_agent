"""Session-local file management for Phase 2 Streamlit app."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timezone
import json
import uuid


@dataclass
class SessionPaths:
    base_dir: Path
    rationale_docx: Path
    task_json: Path
    output_xlsx: Path


class SessionManager:
    def __init__(self, root_dir: Path | None = None) -> None:
        self.root_dir = root_dir or Path("phase_2/sessions")
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def get_or_create_session_id(self, existing_session_id: str | None = None) -> str:
        return existing_session_id or uuid.uuid4().hex[:12]

    def ensure_paths(self, session_id: str) -> SessionPaths:
        base = self.root_dir / session_id
        base.mkdir(parents=True, exist_ok=True)
        return SessionPaths(
            base_dir=base,
            rationale_docx=base / "rationale.docx",
            task_json=base / "task_input.json",
            output_xlsx=base / "results.xlsx",
        )

    def save_uploaded_rationale(self, file_bytes: bytes, session_id: str) -> Path:
        paths = self.ensure_paths(session_id)
        paths.rationale_docx.write_bytes(file_bytes)
        return paths.rationale_docx

    def save_task_json(self, task: dict, session_id: str) -> Path:
        paths = self.ensure_paths(session_id)
        payload = {
            **task,
            "_saved_at_utc": datetime.now(timezone.utc).isoformat(),
        }
        with paths.task_json.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        return paths.task_json
