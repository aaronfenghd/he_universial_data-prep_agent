"""Deterministic, lightweight parser from chat text -> Phase 1 task structure."""

from __future__ import annotations

import re
from typing import Any

TASK_KEYS = [
    "parameter_question",
    "population",
    "line_of_therapy",
    "geography",
    "preferred_study_type",
    "exclusion_rules",
    "notes",
]


def empty_task() -> dict[str, Any]:
    return {
        "parameter_question": "",
        "population": "",
        "line_of_therapy": "",
        "geography": "",
        "preferred_study_type": "",
        "exclusion_rules": [],
        "notes": "",
    }


def _normalize_space(text: str) -> str:
    return " ".join(text.strip().split())


def parse_natural_language_request(message: str) -> dict[str, Any]:
    """Best-effort extraction using simple heuristics.

    Intentionally transparent and easy to improve; does not require an LLM.
    """
    message_clean = _normalize_space(message)
    lower = message_clean.lower()

    task = empty_task()
    if message_clean:
        task["parameter_question"] = message_clean

    # Geography heuristics.
    if re.search(r"\b(us|u\.s\.|united states|usa)\b", lower):
        task["geography"] = "United States"
    elif re.search(r"\buk\b|united kingdom", lower):
        task["geography"] = "United Kingdom"
    elif re.search(r"\beu\b|europe", lower):
        task["geography"] = "Europe"

    # Line of therapy heuristics.
    if re.search(r"\b(2l\+|2l|second line|later line|line and later)\b", lower):
        task["line_of_therapy"] = "Second line and later"
    elif re.search(r"\b1l\+|first line\b", lower):
        task["line_of_therapy"] = "First line and later"

    # Study type preference heuristics.
    preferred_flags = []
    if "micro-cost" in lower or "micro costing" in lower:
        preferred_flags.append("Micro-costing studies")
    if "hta" in lower:
        preferred_flags.append("HTA submissions")
    if "cost-effectiveness" in lower or "cea" in lower:
        preferred_flags.append("Cost-effectiveness analyses")
    if "utility" in lower:
        preferred_flags.append("Utility studies")
    if "observational" in lower:
        preferred_flags.append("Observational studies")
    if "he studies" in lower or "health economic" in lower:
        preferred_flags.append("Health economic studies")
    if preferred_flags:
        task["preferred_study_type"] = ", ".join(dict.fromkeys(preferred_flags))

    # Exclusion heuristics: capture after "exclude" and split.
    exclusion_matches = re.findall(r"exclude\s+([^\.]+)", lower)
    exclusions: list[str] = []
    for chunk in exclusion_matches:
        parts = re.split(r",| and ", chunk)
        for item in parts:
            text = item.strip(" .;")
            if text:
                exclusions.append(f"Exclude {text}")
    if exclusions:
        task["exclusion_rules"] = list(dict.fromkeys(exclusions))

    # Population hints.
    if "advanced nsclc" in lower or "metastatic nsclc" in lower:
        task["population"] = "Adults with advanced or metastatic NSCLC"

    # Notes/priorities heuristics.
    if "prioritize" in lower or "prefer" in lower:
        task["notes"] = "User specified preferences/priorities in the request."

    return task


def merge_task_updates(current: dict[str, Any], new_data: dict[str, Any]) -> dict[str, Any]:
    """Merge parser output into an existing task without overwriting useful data."""
    merged = {**empty_task(), **current}
    for key in TASK_KEYS:
        if key == "exclusion_rules":
            existing = merged.get("exclusion_rules", []) or []
            incoming = new_data.get("exclusion_rules", []) or []
            merged["exclusion_rules"] = list(dict.fromkeys([*existing, *incoming]))
            continue

        existing_value = str(merged.get(key, "")).strip()
        incoming_value = str(new_data.get(key, "")).strip()
        if not existing_value and incoming_value:
            merged[key] = incoming_value
    return merged


def detect_missing_fields(task: dict[str, Any]) -> list[str]:
    missing = []
    if not str(task.get("parameter_question", "")).strip():
        missing.append("parameter_question")
    return missing
