"""Convert rationale .docx files to best-effort machine-readable prep direction JSON."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json

from docx import Document


def convert_docx_to_prep_direction(input_docx: Path, output_json: Path) -> dict:
    """Extract text and heading-like sections from a .docx file.

    This is intentionally best-effort for Phase 1 and does not enforce a strict schema.
    """
    doc = Document(str(input_docx))

    full_text_lines: list[str] = []
    sections: list[dict[str, str]] = []

    current_heading = "General"
    current_content: list[str] = []

    def flush_section() -> None:
        nonlocal current_content
        if current_content:
            sections.append(
                {
                    "heading": current_heading,
                    "content": "\n".join(current_content).strip(),
                }
            )
            current_content = []

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        full_text_lines.append(text)

        style_name = (para.style.name or "").lower() if para.style else ""
        is_heading = style_name.startswith("heading")

        if is_heading:
            flush_section()
            current_heading = text
        else:
            current_content.append(text)

    flush_section()

    payload = {
        "source_file": str(input_docx.name),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "best_effort": True,
        "full_text": "\n".join(full_text_lines).strip(),
        "sections": sections,
    }

    output_json.parent.mkdir(parents=True, exist_ok=True)
    with output_json.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    return payload
