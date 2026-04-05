"""Load prep direction JSON files."""

from __future__ import annotations

from pathlib import Path
import json


def load_prep_direction(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
