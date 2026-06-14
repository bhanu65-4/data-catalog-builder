<<<<<<< HEAD
# data-catalog-builder
=======
Data Catalog Builder (Prototype)

Lightweight prototype that scans a folder of CSVs and SQL databases, builds a JSON catalog (tables, columns, sample values), and provides LLM-based column descriptions with a Streamlit search UI.

Quick start

1. Create a Python virtual environment and install requirements:

```bash
python -m venv .venv
# Windows activate
.venv\\Scripts\\activate
pip install -r requirements.txt
```

2. Generate a catalog from CSVs and (optionally) DBs:

```bash
python cataloger.py --csv-folder data --out catalog.json
```

3. Run the Streamlit UI:

```bash
streamlit run streamlit_app.py -- --catalog catalog.json
```

Notes
- The project includes a lightweight LLM enrichment interface. If you set `OPENAI_API_KEY`, it will attempt to call OpenAI; otherwise a rule-based fallback will generate simple descriptions. You can extend `llm_enrich.py` to use a local Hugging Face model.

Submission checklist (for AI Prototype Challenge)

- **Team info:** Add `team_info.md` with team name and member details.
- **Public GitHub:** Ensure the repo is public before submission.
- **README:** This file contains setup + run instructions.
- **Demo video:** Record a 5–7 minute demo showing end-to-end flow.
- **AI usage note:** See `ai_usage_note.md` for what AI helped and known issues.
- **Prompts:** See `prompts.md` for prompt templates used.
- **Sample data:** The `data/` folder contains sample CSVs used for testing.
- **Outputs:** Generated reports are in `outputs/` (e.g. `final_report.md`, `sample_output.csv`).
- **Tests:** Run `pytest` to validate the happy-path test(s).

>>>>>>> 569797e (Initial commit)
