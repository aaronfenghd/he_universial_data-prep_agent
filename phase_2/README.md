# Phase 2 - Lightweight Chat App (Streamlit)

## What Phase 2 is
Phase 2 is a lightweight conversational layer on top of Phase 1.

- **Phase 1 remains the backend engine** for rationale conversion, PubMed-first search, fallback web search, publication selection, and Excel export.
- **Phase 2 adds chat UX**: natural-language intake, structured input extraction, follow-up prompts, rationale upload handling, run trigger, and result presentation/download.

## How Phase 2 relates to Phase 1
Phase 2 calls `run_phase_1(...)` directly from `phase_1/src/main.py`.
It does not reimplement search/selection/export logic.

## Install dependencies
From repo root:

```bash
python -m pip install -r phase_2/requirements.txt
```

## Launch the app
From repo root:

```bash
streamlit run phase_2/app.py
```

## Chat flow
1. Type a natural-language request in chat.
2. The app extracts a best-effort structured Phase 1 task.
3. The app shows extracted fields and asks only for missing required info.
4. Upload a rationale `.docx` file.
5. Click **Run Phase 1 Workflow**.
6. Review chat-style completion summary and selected publications.
7. Download the generated Excel output.

## Rationale upload
- Upload a `.docx` file in the uploader widget.
- The file is saved in a session-local folder under `phase_2/sessions/<session_id>/`.

## Run + download
After a successful run, the app shows:
- backend metadata (`selected_count`, `selection_status`, `pubmed_count`, `web_fallback_count`, `used_web_fallback`)
- selected publication rows
- a **Download Excel Output** button

## Current limitations
- Parser is heuristic/rules-based and may miss or misclassify details.
- Follow-up prompts are intentionally simple and focus on required info + rationale upload readiness.
- No authentication, multi-user backend service, or database (by design for lightweight Phase 2).
