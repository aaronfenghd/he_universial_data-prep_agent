"""Formatting helpers for chat-style assistant responses in Phase 2."""

from __future__ import annotations

from typing import Any


def format_task_summary(task: dict[str, Any]) -> str:
    exclusions = task.get("exclusion_rules", []) or []
    exclusion_text = ", ".join(exclusions) if exclusions else "(none provided)"

    return (
        "I extracted the following information:\n"
        f"- Parameter question: {task.get('parameter_question') or '(missing)'}\n"
        f"- Population: {task.get('population') or '(optional, not provided)'}\n"
        f"- Line of therapy: {task.get('line_of_therapy') or '(optional, not provided)'}\n"
        f"- Geography: {task.get('geography') or '(optional, not provided)'}\n"
        f"- Preferred study type: {task.get('preferred_study_type') or '(optional, not provided)'}\n"
        f"- Exclusion rules: {exclusion_text}\n"
        f"- Notes: {task.get('notes') or '(optional, not provided)'}"
    )


def format_missing_prompt(missing_fields: list[str], has_rationale: bool) -> str:
    prompts: list[str] = []
    if "parameter_question" in missing_fields:
        prompts.append("Please provide the core parameter question you want to search.")
    if not has_rationale:
        prompts.append("Please upload your rationale Word document (.docx) to continue.")
    if not prompts:
        prompts.append("I have what I need and I am ready to run the workflow.")
    return "\n".join(prompts)


def format_workflow_result(result: dict[str, Any]) -> str:
    meta = result.get("search_meta", {})
    selection_status = result.get("selection_status", {})
    return (
        "The workflow is complete.\n"
        f"- selected_count: {result.get('selected_count', 0)}\n"
        f"- pubmed_count: {meta.get('pubmed_count', 0)}\n"
        f"- web_fallback_count: {meta.get('web_fallback_count', 0)}\n"
        f"- used_web_fallback: {meta.get('used_web_fallback', False)}\n"
        f"- selection_status: {selection_status}"
    )


def format_error_message(exc: Exception) -> str:
    return f"I could not complete the workflow: {type(exc).__name__}: {exc}"
