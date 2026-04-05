# Phase 1 - HE Parameter Preparation Agent

## What Phase 1 does
Phase 1 provides a minimal workflow to:
1. Read a standard task input JSON.
2. Convert a user rationale `.docx` file into a machine-readable prep direction JSON (best effort).
3. Read `AGENT.md` and the prep direction file.
4. Search publications with **PubMed first** and **generic web fallback only if PubMed is insufficient**.
5. Select multiple publications.
6. Export results to Excel.

## Folder layout
- `input/rationale_docs/` - place uploaded rationale `.docx` files here.
- `prep_direction/` - generated prep direction JSON files.
- `outputs/` - exported `.xlsx` files.
- `src/` - Phase 1 Python source code.
- `examples/` - example task/prep direction files.

## Expected task input
Use the standard JSON format:

```json
{
  "parameter_question": "",
  "population": "",
  "line_of_therapy": "",
  "geography": "",
  "preferred_study_type": "",
  "exclusion_rules": [],
  "notes": ""
}
```

Rules:
- `parameter_question` is required.
- Other fields are optional.
- `exclusion_rules` must be a list of strings.

## Install dependencies
From repo root:

```bash
python -m pip install -r phase_1/requirements.txt
```

## Run instructions
### Option A: Use an existing prep direction JSON
```bash
python -m phase_1.src.main \
  --task-json phase_1/examples/example_task_input.json \
  --prep-direction-json phase_1/examples/mock_prep_direction.json \
  --output-xlsx phase_1/outputs/example_results.xlsx
```

### Option B: Convert a rationale `.docx` and run end-to-end
```bash
python -m phase_1.src.main \
  --task-json phase_1/examples/example_task_input.json \
  --rationale-docx phase_1/input/rationale_docs/your_rationale.docx \
  --output-xlsx phase_1/outputs/example_results.xlsx
```

## Short worked example
1. Review `phase_1/examples/example_task_input.json`.
2. Run Option A command above.
3. Open `phase_1/outputs/example_results.xlsx`.
4. Confirm exact column order:
   1. Publication Citation
   2. Rationale of Selection
   3. Limitations
   4. Ranking
