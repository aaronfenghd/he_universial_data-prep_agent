# Agent Operating Guidance

## Purpose
This repository contains a lightweight Phase 1 agent for health economics (HE) model parameter evidence preparation.

## Required Phase 1 workflow
1. Read repository instructions first.
2. Read the machine-readable prep direction file generated from the user-uploaded rationale Word document.
3. Use the task input plus prep direction to search and select publications.
4. Export selected publications to Excel.

## Decision behavior
- Follow clear instructions directly.
- If prep direction or task instructions are unclear, incomplete, or ambiguous, do **not** silently finalize a discretionary choice.
- Instead, return a `needs_user_confirmation` state with:
  - a proposed choice, and
  - a short explanation of what confirmation is needed before finalizing.

## Search source priority
- PubMed is the primary source.
- Generic web search is fallback only when PubMed results are insufficient.
