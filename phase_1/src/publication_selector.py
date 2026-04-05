"""Select multiple candidate publications for Phase 1 output."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .publication_search import PublicationRecord
from .task_models import TaskInput

ALLOWED_RANKINGS = {"High", "Medium", "Low"}


@dataclass
class SelectedPublication:
    publication_citation: str
    rationale_of_selection: str
    limitations: str
    ranking: str


def build_citation(record: PublicationRecord) -> str:
    parts = []
    if record.authors:
        parts.append(record.authors)
    if record.year:
        parts.append(f"({record.year})")
    parts.append(record.title)
    if record.journal:
        parts.append(record.journal)
    if record.doi:
        parts.append(f"doi:{record.doi}")
    elif record.pmid:
        parts.append(f"PMID:{record.pmid}")
    return ". ".join(part for part in parts if part)


def select_publications(
    task: TaskInput,
    prep_direction: dict[str, Any],
    candidates: list[PublicationRecord],
) -> tuple[list[SelectedPublication], dict[str, Any]]:
    """Select multiple publications with lightweight heuristic ranking."""
    status = {"state": "ok", "message": ""}

    prep_text = (prep_direction.get("full_text", "") or "").strip()
    if len(prep_text) < 20:
        status = {
            "state": "needs_user_confirmation",
            "message": "Prep direction text is sparse; confirm selection criteria before finalizing.",
            "proposed_choice": "Proceed with top relevance from available metadata.",
        }

    if len(candidates) < 2:
        status = {
            "state": "needs_user_confirmation",
            "message": "Fewer than 2 candidate publications found.",
            "proposed_choice": "Broaden search terms or relax exclusion rules.",
        }

    query_words = set(task.to_query_text().lower().split())

    scored: list[tuple[int, PublicationRecord]] = []
    for record in candidates:
        title_words = set(record.title.lower().split())
        overlap = len(query_words.intersection(title_words))
        source_bonus = 2 if record.source == "pubmed" else 0
        score = overlap + source_bonus
        scored.append((score, record))

    scored.sort(key=lambda x: x[0], reverse=True)

    # Ensure multiple selected publications (target 3 if possible).
    target_n = 3 if len(scored) >= 3 else len(scored)
    selected_records = [r for _, r in scored[:target_n]]

    selected: list[SelectedPublication] = []
    for idx, record in enumerate(selected_records):
        score = scored[idx][0]
        if score >= 5:
            ranking = "High"
        elif score >= 2:
            ranking = "Medium"
        else:
            ranking = "Low"

        if ranking not in ALLOWED_RANKINGS:
            raise ValueError(f"Invalid ranking generated: {ranking}")

        rationale = (
            f"Selected for relevance to '{task.parameter_question}' and metadata match; "
            f"source priority favors PubMed ({record.source})."
        )
        limitation = "Phase 1 heuristic selection; full-text fit and bias appraisal not performed."

        selected.append(
            SelectedPublication(
                publication_citation=build_citation(record),
                rationale_of_selection=rationale,
                limitations=limitation,
                ranking=ranking,
            )
        )

    return selected, status
