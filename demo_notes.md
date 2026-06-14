# Demo Script and Talking Points (5–7 minutes)

1) Opening (20s)
- Team name and members
- One-line problem statement: "We built a Data Catalog Builder that automatically discovers tables and columns from CSV/SQL and generates a searchable catalog with LLM-enriched column descriptions."

2) Show input (30s)
- Show `data/` folder with `customers.csv` and `orders.csv`.
- Mention sample data size and that system supports SQLite/Postgres/CSV.

3) Run pipeline (60s)
- Run `python cataloger.py --csv-folder data --out catalog.json` (show console)
- Explain what it does: discovers tables, reads sample values.

4) Enrich descriptions and generate report (60s)
- Run `python enrich_and_report.py --catalog catalog.json`
- Show `catalog_report.md` and `catalog_report_pretty.html`.
- Point out example descriptions (identifier/email/numeric heuristics).

5) Live UI (90s)
- Launch Streamlit: `python -m streamlit run streamlit_app.py -- --catalog catalog.json`
- Show search box, searching for "email" or "amount".
- Click "Enrich missing descriptions" to demonstrate auto-enrichment.

6) Output and download (30s)
- Show `outputs/sample_output.csv` and `catalog_report_pretty.html` available for download.

7) Tests and docs (30s)
- Run `pytest` to show the happy-path tests pass.
- Point to `README.md`, `prompts.md`, and `ai_usage_note.md`.

8) Closing (20s)
- Limitations, next steps (PII detection, better LLM prompts, integrate Postgres), and where code lives (GitHub link).

Tips: record the terminal and browser window; narrate each command and why it matters; keep pacing steady to fit within 7 minutes.
