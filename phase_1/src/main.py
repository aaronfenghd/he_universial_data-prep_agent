"""Phase 1 entrypoint: task + rationale prep direction -> search -> selection -> Excel."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .doc_to_prep_direction import convert_docx_to_prep_direction
from .excel_exporter import export_to_excel, validate_excel
from .prep_direction_loader import load_prep_direction
from .publication_search import PublicationSearcher
from .publication_selector import select_publications
from .task_models import TaskInput


def read_agent_guidance(agent_md_path: Path) -> str:
    """Read AGENT.md so workflow explicitly includes repo-level guidance."""
    if not agent_md_path.exists():
        return ""
    return agent_md_path.read_text(encoding="utf-8")


def run_phase_1(
    task_json_path: Path,
    rationale_docx_path: Path | None,
    prep_direction_json_path: Path | None,
    output_xlsx_path: Path,
) -> dict:
    task = TaskInput.from_json_file(task_json_path)

    if rationale_docx_path is not None:
        if not rationale_docx_path.exists():
            raise FileNotFoundError(f"Rationale docx not found: {rationale_docx_path}")
        prep_direction_json_path = (
            Path("phase_1/prep_direction") / f"{rationale_docx_path.stem}_prep_direction.json"
        )
        convert_docx_to_prep_direction(rationale_docx_path, prep_direction_json_path)

    if prep_direction_json_path is None:
        raise ValueError("Provide either --rationale-docx or --prep-direction-json.")

    prep_direction = load_prep_direction(prep_direction_json_path)

    # Explicitly read AGENT.md per Phase 1 behavior requirement.
    agent_guidance = read_agent_guidance(Path("AGENT.md"))

    searcher = PublicationSearcher()
    candidates, search_meta = searcher.search(task=task, prep_direction=prep_direction)

    selected, selection_status = select_publications(task, prep_direction, candidates)

    if len(selected) < 2:
        selection_status = {
            "state": "needs_user_confirmation",
            "message": "The workflow requires multiple publications; fewer than 2 were selected.",
            "proposed_choice": "Refine query inputs and rerun.",
        }

    export_to_excel(selected, output_xlsx_path)
    validate_excel(output_xlsx_path)

    return {
        "task_input": str(task_json_path),
        "prep_direction": str(prep_direction_json_path),
        "output_excel": str(output_xlsx_path),
        "search_meta": search_meta,
        "selection_status": selection_status,
        "selected_count": len(selected),
        "agent_md_read": bool(agent_guidance),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Phase 1 HE parameter prep workflow.")
    parser.add_argument(
        "--task-json",
        type=Path,
        required=True,
        help="Path to task input JSON.",
    )
    parser.add_argument(
        "--rationale-docx",
        type=Path,
        default=None,
        help="Optional .docx rationale file in phase_1/input/rationale_docs/.",
    )
    parser.add_argument(
        "--prep-direction-json",
        type=Path,
        default=None,
        help="Optional existing prep direction JSON file.",
    )
    parser.add_argument(
        "--output-xlsx",
        type=Path,
        default=Path("phase_1/outputs/phase_1_results.xlsx"),
        help="Output Excel path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_phase_1(
        task_json_path=args.task_json,
        rationale_docx_path=args.rationale_docx,
        prep_direction_json_path=args.prep_direction_json,
        output_xlsx_path=args.output_xlsx,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
